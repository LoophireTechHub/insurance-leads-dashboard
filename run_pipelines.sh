#!/bin/bash
# Run both insurance lead pipelines with Python 3.11

echo "========================================="
echo "Insurance Leads Pipeline Runner"
echo "========================================="
echo ""

# Activate Python 3.11 virtual environment
source venv311/bin/activate

# Run enhanced multi-signal pipeline
echo "Running enhanced pipeline (multi-signal detection)..."
python insurance_leads_enhanced.py

if [ $? -eq 0 ]; then
    echo "✅ Enhanced pipeline completed successfully"

    # Generate enhanced dashboard
    echo ""
    echo "Generating enhanced dashboard..."
    python generate_enhanced_dashboard.py

    echo ""
    echo "========================================="
    echo "✅ All pipelines completed!"
    echo "========================================="
    echo ""
    echo "📊 View dashboards:"
    echo "   Enhanced: docs/enhanced.html"
    echo ""
else
    echo "❌ Enhanced pipeline failed"
    exit 1
fi
