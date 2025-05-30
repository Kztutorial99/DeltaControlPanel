
#!/bin/bash

echo "🚀 Installing DeltaPro Control Panel..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Update database schema
echo "🗄️ Updating database schema..."
python update_schema.py

# Create admin user
echo "👤 Setting up admin user..."
python create_admin.py

echo "✅ Installation completed successfully!"
echo ""
echo "🎉 DeltaPro Control Panel is ready to use!"
echo "📝 Admin credentials have been saved to admin_info.py"
echo "🔧 You can now run the application with: python main.py"
