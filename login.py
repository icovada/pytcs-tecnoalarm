from pytcs_tecnoalarm import TCSSession
from pytcs_tecnoalarm.exceptions import OTPException
from getpass import getpass
import os

def get_credentials():
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")
    return email, password

def main():
    # Check for environment variables
    session_key = os.environ.get('SESSION_KEY')
    appid = os.environ.get('APPID')

    if session_key and appid:
        print("Using session key and appid from environment variables")
        session = TCSSession(session_key, appid)
    else:
        print("No session key/appid found in environment, using login flow")
        email, password = get_credentials()
        session = TCSSession()
        
        try:
            session.login(email, password)
        except OTPException:
            print("\nOTP required for this account.")
            otp = input("Please enter your OTP: ").strip()
            session.login(email, password, otp)

        print("\nLogin successful!")
        print(f"Token: {session.token}")
        print(f"App ID: {session.appid}")
    
    # Get centrali with error checking
    session.get_centrali()
    centrali = session.centrali
    
    if centrali is None:
        print("Error: Unable to get centrali data (returned None)")
        return session
        
    if not centrali:  # Empty list/array
        print("No centrali data found (empty list)")
        return session
    
    for i, centrale in enumerate(centrali, 1):
        print(f"\nCentrale #{i}:")
        print(f"- {centrali[centrale].tp.description}: SERIAL={centrale}")
    
    return session

if __name__ == "__main__":
    main()