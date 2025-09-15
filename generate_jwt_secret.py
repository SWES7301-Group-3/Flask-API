import secrets

# Generate a shared JWT secret
shared_jwt_secret = secrets.token_urlsafe(64)

print("🔐 Shared JWT Secret for Django and Flask")
print("=" * 50)
print(f"JWT_SECRET_KEY={shared_jwt_secret}")
print("\n📝 Add this EXACT line to both .env files:")
print(f"JWT_SECRET_KEY={shared_jwt_secret}")
print("\n📂 File locations:")
print("- Django-ecomm/.env")
print("- Flask-API/.env")
print("\n⚠️  Keep this secret secure and never commit to Git!")