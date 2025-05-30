import requests
import json
import random
import string
from datetime import datetime
import os

class OTPProviderManager:
    """Manager class for OTP provider integrations"""
    
    def __init__(self):
        self.providers = {
            'tokopedia': self._tokopedia_request,
            'klikdokter': self._klikdokter_request,
            'alodokter': self._alodokter_request,
            'bukalapak': self._bukalapak_request,
            'shopee': self._shopee_request,
            'gojek': self._gojek_request,
            'grab': self._grab_request,
            'traveloka': self._traveloka_request
        }
    
    def request_otp(self, provider_name, phone_number):
        """Request OTP from specified provider"""
        provider_name = provider_name.lower()
        
        if provider_name not in self.providers:
            return {
                'success': False,
                'error': f'Provider {provider_name} not supported'
            }
        
        try:
            return self.providers[provider_name](phone_number)
        except Exception as e:
            return {
                'success': False,
                'error': f'Provider error: {str(e)}'
            }
    
    def get_supported_providers(self):
        """Get list of supported providers"""
        return list(self.providers.keys())
    
    def _generate_fake_otp(self):
        """Generate a fake OTP for demonstration"""
        return ''.join(random.choices(string.digits, k=6))
    
    def _tokopedia_request(self, phone_number):
        """Tokopedia OTP request"""
        try:
            # Clean phone number
            phone = phone_number.replace('+62', '0').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            data = {
                'phone': phone,
                'h-captcha-response': '',
                'original_param': '',
                'user_id': '',
                'signature': ''
            }
            
            # Make request to Tokopedia OTP API
            response = requests.post(
                'https://accounts.tokopedia.com/otp/c/page',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'tokopedia'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Unknown error from Tokopedia')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _klikdokter_request(self, phone_number):
        """KlikDokter OTP request"""
        try:
            phone = phone_number.replace('+62', '62').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Origin': 'https://www.klikdokter.com'
            }
            
            data = {
                'phone_number': phone,
                'send_method': 'sms'
            }
            
            response = requests.post(
                'https://api.klikdokter.com/v1/auth/send-otp',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'klikdokter'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Unknown error from KlikDokter')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'KlikDokter error: {str(e)}'
            }
    
    def _alodokter_request(self, phone_number):
        """Alodokter OTP request"""
        try:
            phone = phone_number.replace('+62', '62').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'user_phone': phone
            }
            
            response = requests.post(
                'https://www.alodokter.com/login/send-otp',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'alodokter'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Unknown error from Alodokter')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Alodokter error: {str(e)}'
            }
    
    def _bukalapak_request(self, phone_number):
        """Bukalapak OTP request"""
        try:
            phone = phone_number.replace('+62', '').replace(' ', '').replace('-', '')
            if phone.startswith('0'):
                phone = '62' + phone[1:]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'phone': phone
            }
            
            response = requests.post(
                'https://api.bukalapak.com/v2/authenticate.json',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'OK':
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'bukalapak'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Unknown error from Bukalapak')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Bukalapak error: {str(e)}'
            }
    
    def _shopee_request(self, phone_number):
        """Shopee OTP request"""
        try:
            phone = phone_number.replace('+62', '62').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Referer': 'https://shopee.co.id/'
            }
            
            data = {
                'phone': phone,
                'phone_code': '62'
            }
            
            response = requests.post(
                'https://shopee.co.id/api/v2/authentication/send_code',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error') == 0:
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'shopee'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error_msg', 'Unknown error from Shopee')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Shopee error: {str(e)}'
            }
    
    def _gojek_request(self, phone_number):
        """Gojek OTP request"""
        try:
            phone = phone_number.replace('+62', '').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'phone_number': '+62' + phone if not phone.startswith('62') else '+' + phone
            }
            
            response = requests.post(
                'https://api.gojekapi.com/v5/customers/phone/otp',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'gojek'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('errors', ['Unknown error from Gojek'])[0]
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Gojek error: {str(e)}'
            }
    
    def _grab_request(self, phone_number):
        """Grab OTP request"""
        try:
            phone = phone_number.replace('+62', '62').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'countryCode': 'ID',
                'phoneNumber': phone
            }
            
            response = requests.post(
                'https://p.grabtaxi.com/api/passenger/v2/profiles/register',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('error'):
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'grab'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error from Grab')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Grab error: {str(e)}'
            }
    
    def _traveloka_request(self, phone_number):
        """Traveloka OTP request"""
        try:
            phone = phone_number.replace('+62', '62').replace(' ', '').replace('-', '')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {
                'phone': phone,
                'client_interface': 'mobile'
            }
            
            response = requests.post(
                'https://www.traveloka.com/api/v2/user/registration/phone/otp',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'otp_code': 'Check SMS',
                        'data': result,
                        'provider': 'traveloka'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Unknown error from Traveloka')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Traveloka error: {str(e)}'
            }
