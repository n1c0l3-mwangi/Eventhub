"""
Mobile Money Payment Module
"""

import time
from datetime import datetime

class InternalMobilePaymentModule:
    """
    Processes mobile money payments
    """
    
    @staticmethod
    def process_payment(phone_number, amount):
        """
        Process payment via mobile money
        
        Args:
            phone_number: Customer's phone number
            amount: Amount to charge
            
        Returns:
            (success, transaction_id, message)
        """
        # Basic validation
        if not phone_number or len(phone_number) < 10:
            return False, None, "Invalid phone number"
        
        if amount <= 0:
            return False, None, "Invalid amount"
        
        # Process payment
        time.sleep(2)  # Network delay
        
        # Generate transaction ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        transaction_id = f"MP{timestamp}"
        
        # Payment successful
        return True, transaction_id, "Payment completed successfully"