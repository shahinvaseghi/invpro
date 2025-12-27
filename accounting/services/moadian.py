"""
Moadian Taxpayer System API Service
سرویس API برای ارتباط با سامانه مودیان
"""
import json
import time
import uuid
import logging
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from django.conf import settings
from django.utils import timezone

# Cryptography imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import jwt
from jwt import PyJWK

logger = logging.getLogger('accounting.services.moadian')


class MoadianService:
    """
    سرویس برای ارتباط با سامانه مودیان
    Service for communication with Taxpayer System (سامانه مودیان)
    
    طبق دستورالعمل فنی RC_TICS.IS_v1.3
    """
    
    def __init__(self, fiscal_memory_config):
        """
        Initialize Moadian service with fiscal memory configuration.
        
        Args:
            fiscal_memory_config: FiscalMemoryConfig instance
        """
        self.config = fiscal_memory_config
        self.base_url = fiscal_memory_config.server_url.rstrip('/')
        self.timeout = fiscal_memory_config.api_timeout
        self.fiscal_id = fiscal_memory_config.fiscal_id
        self._private_key = None
        self._public_key = None
        self._certificate = None
        self._server_public_key = None
        self._server_key_id = None
        
        # Load keys and certificate
        self._load_keys()
    
    def _load_keys(self):
        """Load private key, public key, and certificate from config."""
        try:
            # Load private key
            if self.config.private_key:
                private_key_pem = self.config.private_key.encode('utf-8')
                password = self.config.private_key_password.encode('utf-8') if self.config.private_key_password else None
                
                self._private_key = serialization.load_pem_private_key(
                    private_key_pem,
                    password=password,
                    backend=default_backend()
                )
            
            # Load public key
            if self.config.public_key:
                public_key_pem = self.config.public_key.encode('utf-8')
                self._public_key = serialization.load_pem_public_key(
                    public_key_pem,
                    backend=default_backend()
                )
            
            # Load certificate from metadata
            if self.config.metadata and 'certificate' in self.config.metadata:
                cert_pem = self.config.metadata['certificate'].encode('utf-8')
                # Certificate will be used in JWT header
                self._certificate = cert_pem.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error loading keys: {e}")
            raise ValueError(f"خطا در بارگذاری کلیدها: {e}")
    
    def _generate_uid(self) -> str:
        """Generate unique identifier for requests."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    def _normalize_json(self, data: Dict[str, Any]) -> str:
        """
        نرمال‌سازی JSON طبق مستند سامانه مودیان
        Normalize JSON according to Moadian documentation
        """
        # Remove null values and empty strings
        def clean_dict(d):
            if isinstance(d, dict):
                return {
                    k: clean_dict(v) 
                    for k, v in d.items() 
                    if v is not None and v != ''
                }
            elif isinstance(d, list):
                return [clean_dict(item) for item in d if item is not None]
            return d
        
        cleaned = clean_dict(data)
        # Sort keys for consistency
        return json.dumps(cleaned, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    
    def get_nonce(self) -> str:
        """
        دریافت Nonce از سامانه مودیان
        Get nonce from taxpayer system
        
        Returns:
            Nonce string
        """
        url = f"{self.base_url}/req/api/self-tsp/nonce"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('nonce', '')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting nonce: {e}")
            raise ValueError(f"خطا در دریافت Nonce: {e}")
    
    def _create_jwt_payload(self, nonce: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        ساخت JWT Payload
        Create JWT Payload
        
        Args:
            nonce: Nonce received from server
            client_id: Client ID (defaults to fiscal_id)
        
        Returns:
            JWT Payload dictionary
        """
        client_id = client_id or self.fiscal_id
        timestamp = self._get_timestamp()
        
        payload = {
            "clientId": client_id,
            "nonce": nonce,
            "timestamp": timestamp,
        }
        
        return payload
    
    def _create_jwt_header(self) -> Dict[str, Any]:
        """
        ساخت JWT Header با گواهینامه
        Create JWT Header with certificate
        
        Returns:
            JWT Header dictionary
        """
        if not self._certificate:
            raise ValueError("گواهینامه (Certificate) یافت نشد. لطفاً گواهینامه را در تنظیمات اضافه کنید.")
        
        # Extract certificate info (simplified - in production should parse X.509)
        # For now, we'll include the certificate in the header
        header = {
            "alg": "RS256",  # RSA with SHA-256
            "typ": "JWT",
            "x5c": [self._certificate]  # Certificate chain
        }
        
        return header
    
    def _sign_data(self, data: str) -> str:
        """
        امضای دیجیتال داده‌ها با RSA (JWS)
        Digital signature of data using RSA (JWS)
        
        Args:
            data: Data to sign (string)
        
        Returns:
            Base64-encoded signature
        """
        if not self._private_key:
            raise ValueError("کلید خصوصی یافت نشد. لطفاً کلید خصوصی را در تنظیمات اضافه کنید.")
        
        try:
            # Sign data using RSA with SHA-256
            signature = self._private_key.sign(
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Return base64-encoded signature
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.error(f"Error signing data: {e}")
            raise ValueError(f"خطا در امضای داده: {e}")
    
    def create_jwt_token(self, nonce: Optional[str] = None) -> str:
        """
        ساخت JWT Token کامل (JWS)
        Create complete JWT Token (JWS)
        
        Args:
            nonce: Nonce (if not provided, will be fetched from server)
        
        Returns:
            JWT token string
        """
        # Get nonce if not provided
        if nonce is None:
            nonce = self.get_nonce()
        
        # Create payload
        payload = self._create_jwt_payload(nonce)
        
        # Create header
        header = self._create_jwt_header()
        
        # Create JWT using PyJWT
        try:
            token = jwt.encode(
                payload,
                self._private_key,
                algorithm="RS256",
                headers=header
            )
            return token
        except Exception as e:
            logger.error(f"Error creating JWT: {e}")
            raise ValueError(f"خطا در ساخت JWT: {e}")
    
    def get_server_information(self) -> Dict[str, Any]:
        """
        دریافت اطلاعات سرور مودیان و Public Key سازمان
        Get server information and organization public key
        
        Returns:
            Dict containing server information including public key
        """
        url = f"{self.base_url}/req/api/self-tsp/server-information"
        
        try:
            # Get nonce and create JWT
            nonce = self.get_nonce()
            token = self.create_jwt_token(nonce)
            
            # Make authenticated request
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extract and store server public key
            if 'publicKey' in data:
                self._server_public_key = data['publicKey']
                self._server_key_id = data.get('keyId', '')
                
                # Store in config metadata for future use
                if not self.config.metadata:
                    self.config.metadata = {}
                self.config.metadata['server_public_key'] = self._server_public_key
                self.config.metadata['server_key_id'] = self._server_key_id
                self.config.save(update_fields=['metadata'])
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting server information: {e}")
            raise ValueError(f"خطا در دریافت اطلاعات سرور: {e}")
    
    def _load_server_public_key(self):
        """Load server public key from metadata or fetch from server."""
        if self._server_public_key:
            return
        
        # Try to load from metadata
        if self.config.metadata and 'server_public_key' in self.config.metadata:
            self._server_public_key = self.config.metadata['server_public_key']
            self._server_key_id = self.config.metadata.get('server_key_id', '')
            return
        
        # Fetch from server if not in metadata
        self.get_server_information()
    
    def _generate_symmetric_key(self) -> bytes:
        """
        تولید کلید متقارن AES-256
        Generate symmetric AES-256 key
        
        Returns:
            32-byte key for AES-256
        """
        return AESGCM.generate_key(bit_length=256)
    
    def _encrypt_data(self, data: str, encryption_key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        رمزگذاری داده‌ها با JWE (JSON Web Encryption)
        Encrypt data using JWE (JSON Web Encryption)
        
        طبق مستند:
        1. تولید کلید متقارن AES-256
        2. رمزگذاری داده با AES-GCM
        3. رمزگذاری کلید متقارن با RSA-OAEP-256 (با Public Key سازمان)
        
        Args:
            data: Data to encrypt (string)
            encryption_key_id: Key ID for encryption (optional)
        
        Returns:
            Dict containing encrypted data structure
        """
        # Load server public key if not loaded
        self._load_server_public_key()
        
        if not self._server_public_key:
            raise ValueError("کلید عمومی سرور یافت نشد. لطفاً ابتدا اطلاعات سرور را دریافت کنید.")
        
        try:
            # 1. Generate symmetric key (AES-256)
            symmetric_key = self._generate_symmetric_key()
            
            # 2. Encrypt data with AES-GCM
            aesgcm = AESGCM(symmetric_key)
            nonce = AESGCM.generate_nonce(bit_length=96)  # 12 bytes for GCM
            ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
            
            # Extract ciphertext and authentication tag
            # GCM produces ciphertext + tag, we need to separate them
            # Tag is last 16 bytes
            tag_length = 16
            encrypted_data = ciphertext[:-tag_length]
            auth_tag = ciphertext[-tag_length:]
            
            # 3. Encrypt symmetric key with RSA-OAEP-256
            # Load server public key
            server_pub_key = serialization.load_pem_public_key(
                self._server_public_key.encode('utf-8'),
                backend=default_backend()
            )
            
            encrypted_symmetric_key = server_pub_key.encrypt(
                symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 4. Build JWE structure
            key_id = encryption_key_id or self._server_key_id or ""
            
            jwe_data = {
                "encryptionKeyId": key_id,
                "symmetricKey": base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
                "iv": base64.b64encode(nonce).decode('utf-8'),
                "data": base64.b64encode(encrypted_data).decode('utf-8'),
                "authenticationTag": base64.b64encode(auth_tag).decode('utf-8'),
            }
            
            return jwe_data
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise ValueError(f"خطا در رمزگذاری داده: {e}")
    
    def _decrypt_data(self, encrypted_data: Dict[str, Any]) -> str:
        """
        رمزگشایی داده‌های JWE
        Decrypt JWE data
        
        Args:
            encrypted_data: Encrypted data structure from JWE
        
        Returns:
            Decrypted data string
        """
        if not self._private_key:
            raise ValueError("کلید خصوصی یافت نشد.")
        
        try:
            # Decrypt symmetric key
            encrypted_symmetric_key = base64.b64decode(encrypted_data['symmetricKey'])
            symmetric_key = self._private_key.decrypt(
                encrypted_symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data
            iv = base64.b64decode(encrypted_data['iv'])
            data = base64.b64decode(encrypted_data['data'])
            auth_tag = base64.b64decode(encrypted_data['authenticationTag'])
            
            # Combine data and tag for GCM
            ciphertext = data + auth_tag
            
            aesgcm = AESGCM(symmetric_key)
            decrypted = aesgcm.decrypt(iv, ciphertext, None)
            
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise ValueError(f"خطا در رمزگشایی داده: {e}")
    
    def _build_packet(
        self,
        packet_type: str,
        data: Dict[str, Any],
        retry: bool = False,
        uid: Optional[str] = None,
        encrypt: bool = True
    ) -> Dict[str, Any]:
        """
        ساخت بسته (PACKET) طبق مستند
        Build PACKET according to documentation
        
        Args:
            packet_type: Type of packet (e.g., "INVOICE.V01")
            data: Data to include in packet
            retry: Whether this is a retry
            uid: Unique identifier (auto-generated if not provided)
            encrypt: Whether to encrypt the data
        
        Returns:
            Packet dictionary
        """
        if uid is None:
            uid = self._generate_uid()
        
        # Normalize data
        normalized_data = self._normalize_json(data)
        
        # Encrypt if needed
        encryption_info = {}
        if encrypt:
            encrypted = self._encrypt_data(normalized_data)
            encryption_info = {
                "encryptionKeyId": encrypted["encryptionKeyId"],
                "symmetricKey": encrypted["symmetricKey"],
                "iv": encrypted["iv"],
            }
            # Use encrypted data
            data_to_sign = encrypted["data"] + encrypted["authenticationTag"]
        else:
            data_to_sign = normalized_data
        
        # Sign data
        signature = self._sign_data(data_to_sign)
        
        packet_data = {
            "uid": uid,
            "packetType": packet_type,
            "retry": retry,
            "data": base64.b64encode(normalized_data.encode('utf-8')).decode('utf-8') if encrypt else normalized_data,
            "encryptionKeyId": encryption_info.get("encryptionKeyId", ""),
            "symmetricKey": encryption_info.get("symmetricKey", ""),
            "iv": encryption_info.get("iv", ""),
            "fiscalId": self.fiscal_id,
            "dataSignature": signature
        }
        
        return packet_data
    
    def _make_request(
        self,
        endpoint: str,
        packet: Dict[str, Any],
        sync: bool = False,
        use_auth: bool = True
    ) -> Dict[str, Any]:
        """
        ارسال درخواست به API
        Send request to API
        
        Args:
            endpoint: API endpoint
            packet: Packet data
            sync: Whether to use sync endpoint
            use_auth: Whether to use JWT authentication
        
        Returns:
            Response data
        """
        url = f"{self.base_url}/req/api/tsp"
        if sync:
            url += f"/sync/{endpoint}"
        else:
            url += f"/async/{endpoint}"
        
        timestamp = self._get_timestamp()
        request_trace_id = self._generate_uid()
        
        headers = {
            'requestTraceId': request_trace_id,
            'timestamp': str(timestamp),
            'Content-Type': 'application/json',
        }
        
        # Add JWT authentication if needed
        if use_auth:
            try:
                nonce = self.get_nonce()
                token = self.create_jwt_token(nonce)
                headers['Authorization'] = f'Bearer {token}'
            except Exception as e:
                logger.warning(f"Could not add JWT authentication: {e}")
        
        request_body = {
            "time": timestamp,
            "packet": packet
        }
        
        try:
            response = requests.post(
                url,
                json=request_body,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in Moadian API request: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_token(self) -> Dict[str, Any]:
        """
        دریافت توکن
        Get token from taxpayer system
        
        Returns:
            Dict containing token information
        """
        packet = self._build_packet("GET_TOKEN", {}, encrypt=False)
        return self._make_request("GET_TOKEN", packet, sync=True, use_auth=False)
    
    def submit_invoice(
        self,
        invoice_data: Dict[str, Any],
        uid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ارسال صورتحساب (متد غیرهمگام)
        Submit invoice (async method)
        
        Args:
            invoice_data: داده‌های صورتحساب
            uid: شناسه یکتا (اختیاری)
        
        Returns:
            Dict containing submission response
        """
        packet = self._build_packet("INVOICE.V01", invoice_data, uid=uid, encrypt=True)
        return self._make_request("INVOICE.V01", packet, sync=False, use_auth=True)
    
    def get_invoice_status(self, uid: str) -> Dict[str, Any]:
        """
        استعلام وضعیت صورتحساب (متد همگام)
        Get invoice status (sync method)
        
        Args:
            uid: شناسه یکتای صورتحساب
        
        Returns:
            Dict containing invoice status
        """
        packet = self._build_packet(
            "GET_INVOICE_STATUS",
            {"uid": uid},
            encrypt=False
        )
        return self._make_request("GET_INVOICE_STATUS", packet, sync=True, use_auth=True)
    
    def inquiry_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        استعلام با UID
        Inquiry by UID
        
        Args:
            uid: شناسه یکتا
        
        Returns:
            Dict containing inquiry result
        """
        packet = self._build_packet(
            "INQUIRY_BY_UID",
            {"uid": uid},
            encrypt=False
        )
        return self._make_request("INQUIRY_BY_UID", packet, sync=True, use_auth=True)
    
    def inquiry_by_time_range(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        استعلام با بازه زمانی
        Inquiry by time range
        
        Args:
            start_date: تاریخ شروع (format: YYYYMMDD)
            end_date: تاریخ پایان (format: YYYYMMDD)
        
        Returns:
            Dict containing inquiry results
        """
        packet = self._build_packet(
            "INQUIRY_BY_TIME_RANGE",
            {
                "startDate": start_date,
                "endDate": end_date
            },
            encrypt=False
        )
        return self._make_request("INQUIRY_BY_TIME_RANGE", packet, sync=True, use_auth=True)
    
    def get_fiscal_information(self) -> Dict[str, Any]:
        """
        دریافت اطلاعات حافظه مالیاتی
        Get fiscal memory information
        """
        packet = self._build_packet("GET_FISCAL_INFORMATION", {}, encrypt=False)
        return self._make_request("GET_FISCAL_INFORMATION", packet, sync=True, use_auth=True)
    
    def get_service_stuff_list(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """
        دریافت لیست کامل شناسه کالا/خدمات و نرخ مالیاتی
        Get complete list of item/service IDs and tax rates
        """
        packet = self._build_packet(
            "GET_SERVICE_STUFF_LIST",
            {"page": page, "size": size},
            encrypt=False
        )
        return self._make_request("GET_SERVICE_STUFF_LIST", packet, sync=True, use_auth=True)
    
    def get_economic_code_information(self, economic_code: str) -> Dict[str, Any]:
        """
        استعلام اطلاعات شماره اقتصادی
        Get economic code information
        """
        packet = self._build_packet(
            "GET_ECONOMIC_CODE_INFORMATION",
            {"economicCode": economic_code},
            encrypt=False
        )
        return self._make_request("GET_ECONOMIC_CODE_INFORMATION", packet, sync=True, use_auth=True)
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        اعتبارسنجی داده‌های صورتحساب قبل از ارسال
        Validate invoice data before submission
        
        Args:
            invoice_data: داده‌های صورتحساب
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # بررسی فیلدهای اجباری
        required_fields = ['header', 'body']
        for field in required_fields:
            if field not in invoice_data:
                errors.append(f"فیلد '{field}' اجباری است")
        
        # بررسی ساختار header
        if 'header' in invoice_data:
            header = invoice_data['header']
            header_required = ['taxId', 'indatim', 'indati2m', 'inty', 'inno', 'irtaxid', 'inp', 'ins', 'tins']
            for field in header_required:
                if field not in header:
                    errors.append(f"فیلد 'header.{field}' اجباری است")
        
        # بررسی ساختار body
        if 'body' in invoice_data:
            body = invoice_data['body']
            if not isinstance(body, list) or len(body) == 0:
                errors.append("فیلد 'body' باید یک آرایه غیرخالی باشد")
            else:
                # بررسی هر آیتم در body
                for idx, item in enumerate(body):
                    item_required = ['sstid', 'sstt', 'am', 'mu', 'fee', 'cfeeon', 'cut', 'exr', 'prdis', 'dis', 'adis', 'vra', 'vam', 'odt', 'odr', 'odam', 'olt', 'olr', 'olam', 'consfee', 'spro', 'bros', 'tcpbs', 'cop', 'vop', 'bsrn', 'tsstam']
                    for field in item_required:
                        if field not in item:
                            errors.append(f"فیلد 'body[{idx}].{field}' اجباری است")
        
        return len(errors) == 0, errors
