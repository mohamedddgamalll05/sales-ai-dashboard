#!/bin/bash
# Setting MongoDB URI Environment Variable

echo "========================================"
echo "Setting MongoDB URI Environment Variable"
echo "========================================"
echo ""

# Set MongoDB URI for current session
export MONGODB_URI="mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority"

# Add to .bashrc or .zshrc for persistence
if [ -f ~/.bashrc ]; then
    echo "" >> ~/.bashrc
    echo "# MongoDB URI for Sales AI Dashboard" >> ~/.bashrc
    echo "export MONGODB_URI=\"mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority\"" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
elif [ -f ~/.zshrc ]; then
    echo "" >> ~/.zshrc
    echo "# MongoDB URI for Sales AI Dashboard" >> ~/.zshrc
    echo "export MONGODB_URI=\"mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority\"" >> ~/.zshrc
    echo "✅ Added to ~/.zshrc"
fi

echo ""
echo "✅ MongoDB URI has been set!"
echo ""
echo "The environment variable is now active in this session."
echo "For persistence, it has been added to your shell configuration file."
echo ""
echo "You can verify with:"
echo "  echo \$MONGODB_URI"
echo ""

