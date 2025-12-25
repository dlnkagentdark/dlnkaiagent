"""
dLNk AI Bridge - Protobuf Encoder
=================================
Lightweight encoder for Antigravity/Jetski Protobuf messages.

Based on: /source-files/dlnk_core/dlnk_antigravity_bridge.py

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import struct
import uuid
from typing import Optional


class ProtoEncoder:
    """
    Lightweight encoder for Antigravity Protobuf messages
    
    This encoder creates binary protobuf payloads without requiring
    the full protobuf library, making it lightweight and portable.
    
    Wire Types:
    - 0: Varint (int32, int64, uint32, uint64, sint32, sint64, bool, enum)
    - 1: 64-bit (fixed64, sfixed64, double)
    - 2: Length-delimited (string, bytes, embedded messages, packed repeated fields)
    - 5: 32-bit (fixed32, sfixed32, float)
    """
    
    @staticmethod
    def _encode_varint(value: int) -> bytearray:
        """
        Encode integer as varint (variable-length integer)
        
        Args:
            value: Integer to encode
        
        Returns:
            Encoded bytes
        """
        bytes_out = bytearray()
        while value > 0x7F:
            bytes_out.append((value & 0x7F) | 0x80)
            value >>= 7
        bytes_out.append(value)
        return bytes_out
    
    @staticmethod
    def _decode_varint(data: bytes, offset: int = 0) -> tuple:
        """
        Decode varint from bytes
        
        Args:
            data: Bytes to decode
            offset: Starting offset
        
        Returns:
            Tuple of (decoded value, bytes consumed)
        """
        result = 0
        shift = 0
        consumed = 0
        
        while offset + consumed < len(data):
            byte = data[offset + consumed]
            consumed += 1
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        
        return result, consumed
    
    @staticmethod
    def _encode_field(field_no: int, wire_type: int, data: bytes) -> bytes:
        """
        Encode a protobuf field
        
        Args:
            field_no: Field number
            wire_type: Wire type (0, 1, 2, or 5)
            data: Field data
        
        Returns:
            Encoded field bytes
        """
        tag = (field_no << 3) | wire_type
        return bytes(ProtoEncoder._encode_varint(tag)) + data
    
    @staticmethod
    def encode_string(field_no: int, value: str) -> bytes:
        """
        Encode string field (wire type 2)
        
        Args:
            field_no: Field number
            value: String value
        
        Returns:
            Encoded bytes
        """
        data = value.encode('utf-8')
        length = ProtoEncoder._encode_varint(len(data))
        return ProtoEncoder._encode_field(field_no, 2, bytes(length) + data)
    
    @staticmethod
    def encode_bytes(field_no: int, value: bytes) -> bytes:
        """
        Encode bytes field (wire type 2)
        
        Args:
            field_no: Field number
            value: Bytes value
        
        Returns:
            Encoded bytes
        """
        length = ProtoEncoder._encode_varint(len(value))
        return ProtoEncoder._encode_field(field_no, 2, bytes(length) + value)
    
    @staticmethod
    def encode_message(field_no: int, data: bytes) -> bytes:
        """
        Encode nested message field (wire type 2)
        
        Args:
            field_no: Field number
            data: Message data
        
        Returns:
            Encoded bytes
        """
        length = ProtoEncoder._encode_varint(len(data))
        return ProtoEncoder._encode_field(field_no, 2, bytes(length) + data)
    
    @staticmethod
    def encode_bool(field_no: int, value: bool) -> bytes:
        """
        Encode boolean field (wire type 0)
        
        Args:
            field_no: Field number
            value: Boolean value
        
        Returns:
            Encoded bytes
        """
        data = bytearray([1 if value else 0])
        return ProtoEncoder._encode_field(field_no, 0, bytes(data))
    
    @staticmethod
    def encode_int32(field_no: int, value: int) -> bytes:
        """
        Encode int32 field (wire type 0)
        
        Args:
            field_no: Field number
            value: Integer value
        
        Returns:
            Encoded bytes
        """
        return ProtoEncoder._encode_field(field_no, 0, bytes(ProtoEncoder._encode_varint(value)))
    
    @staticmethod
    def encode_float(field_no: int, value: float) -> bytes:
        """
        Encode float field (wire type 5)
        
        Args:
            field_no: Field number
            value: Float value
        
        Returns:
            Encoded bytes
        """
        data = struct.pack('<f', value)
        return ProtoEncoder._encode_field(field_no, 5, data)
    
    @staticmethod
    def encode_double(field_no: int, value: float) -> bytes:
        """
        Encode double field (wire type 1)
        
        Args:
            field_no: Field number
            value: Double value
        
        Returns:
            Encoded bytes
        """
        data = struct.pack('<d', value)
        return ProtoEncoder._encode_field(field_no, 1, data)
    
    @staticmethod
    def build_cascade_request(
        cascade_id: str,
        prompt: str,
        access_token: str,
        session_id: Optional[str] = None
    ) -> bytes:
        """
        Build SendUserCascadeMessageRequest binary payload
        
        This is the main request format for Antigravity gRPC API.
        
        Field Mapping (based on reverse engineering):
        1: cascade_id (string)
        2: items (TextOrScopeItem - Repeated)
        3: metadata (Metadata)
        4: experiment_config (ExperimentConfig)
        7: cascade_config (CascadeConfig)
        8: blocking (bool)
        
        Args:
            cascade_id: Unique cascade/conversation ID
            prompt: User message/prompt
            access_token: OAuth access token
            session_id: Optional session ID (generated if not provided)
        
        Returns:
            gRPC-framed binary payload ready to send
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 1. Encode Items (Field 2) - Text Message
        # TextOrScopeItem structure:
        #   1: scope_item (ScopeItem)
        #      9: text (string) - The actual prompt text
        text_chunk = ProtoEncoder.encode_string(9, prompt)
        scope_item = ProtoEncoder.encode_message(1, text_chunk)
        items_payload = ProtoEncoder.encode_message(2, scope_item)
        
        # 2. Encode Metadata (Field 3)
        # Metadata structure:
        #   1: access_token (string)
        #   4: session_id (string)
        meta_token = ProtoEncoder.encode_string(1, access_token)
        meta_session = ProtoEncoder.encode_string(4, session_id)
        meta_payload = ProtoEncoder.encode_message(3, meta_token + meta_session)
        
        # 3. Encode ExperimentConfig (Field 4) - Empty for now
        exp_payload = ProtoEncoder.encode_message(4, b"")
        
        # 4. Encode CascadeConfig (Field 7)
        # CascadeConfig structure:
        #   1: model_config (ModelConfig)
        #      1: model_alias (string) - Empty for default model
        model_alias = ProtoEncoder.encode_message(1, b"")
        cascade_config = ProtoEncoder.encode_message(1, model_alias)
        config_payload = ProtoEncoder.encode_message(7, cascade_config)
        
        # 5. Build Final Request Payload
        request = (
            ProtoEncoder.encode_string(1, cascade_id) +
            items_payload +
            meta_payload +
            exp_payload +
            config_payload +
            ProtoEncoder.encode_bool(8, True)  # blocking = true
        )
        
        # 6. Add gRPC framing
        # gRPC frame: 1 byte (compressed flag) + 4 bytes (message length BE) + message
        framed = b"\x00" + struct.pack(">I", len(request)) + request
        
        return framed
    
    @staticmethod
    def build_simple_chat_request(
        message: str,
        access_token: str,
        conversation_id: Optional[str] = None
    ) -> bytes:
        """
        Build a simple chat request (alternative format)
        
        Args:
            message: User message
            access_token: OAuth access token
            conversation_id: Optional conversation ID
        
        Returns:
            gRPC-framed binary payload
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        return ProtoEncoder.build_cascade_request(
            cascade_id=conversation_id,
            prompt=message,
            access_token=access_token
        )


class ProtoDecoder:
    """
    Lightweight decoder for Antigravity Protobuf responses
    """
    
    @staticmethod
    def parse_grpc_response(data: bytes) -> Optional[str]:
        """
        Parse gRPC response to extract text content
        
        Args:
            data: Raw gRPC response bytes
        
        Returns:
            Extracted text or None if parsing fails
        """
        try:
            # Skip gRPC frame header (5 bytes)
            # Frame format: 1 byte (compressed flag) + 4 bytes (message length)
            if len(data) < 5:
                return None
            
            compressed = data[0]
            message_length = struct.unpack(">I", data[1:5])[0]
            message = data[5:5 + message_length]
            
            # Extract text from protobuf message
            return ProtoDecoder._extract_text(message)
            
        except Exception as e:
            return None
    
    @staticmethod
    def _extract_text(message: bytes) -> Optional[str]:
        """
        Extract readable text from protobuf message
        
        This is a simplified parser that looks for length-prefixed strings
        in the message. A full implementation would parse the complete
        protobuf structure.
        
        Args:
            message: Protobuf message bytes
        
        Returns:
            Extracted text or None
        """
        text_parts = []
        i = 0
        
        while i < len(message):
            # Check wire type (last 3 bits of tag)
            if i >= len(message):
                break
            
            tag = message[i]
            wire_type = tag & 0x07
            
            if wire_type == 2:  # Length-delimited (string/bytes/message)
                i += 1
                if i >= len(message):
                    break
                
                # Read length (varint)
                length = 0
                shift = 0
                while i < len(message):
                    byte = message[i]
                    i += 1
                    length |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                
                # Extract string content
                if i + length <= len(message) and length > 10:
                    try:
                        text = message[i:i + length].decode('utf-8', errors='ignore')
                        # Filter for readable text
                        if text.isprintable() and len(text.strip()) > 5:
                            text_parts.append(text.strip())
                    except:
                        pass
                
                i += length
            else:
                i += 1
        
        return '\n'.join(text_parts) if text_parts else None
    
    @staticmethod
    def parse_streaming_response(data: bytes) -> list:
        """
        Parse streaming gRPC response (multiple frames)
        
        Args:
            data: Raw streaming response bytes
        
        Returns:
            List of extracted text chunks
        """
        chunks = []
        offset = 0
        
        while offset + 5 <= len(data):
            # Read frame header
            compressed = data[offset]
            message_length = struct.unpack(">I", data[offset + 1:offset + 5])[0]
            
            if offset + 5 + message_length > len(data):
                break
            
            # Extract message
            message = data[offset + 5:offset + 5 + message_length]
            text = ProtoDecoder._extract_text(message)
            
            if text:
                chunks.append(text)
            
            offset += 5 + message_length
        
        return chunks
