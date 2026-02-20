try:
    from app import app
    print("App imported successfully.")
except Exception as e:
    print(f"Error importing app: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
