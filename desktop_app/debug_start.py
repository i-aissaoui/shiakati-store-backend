# debug_start.py
import sys
import traceback

try:
    from main import main
    main()
except Exception as e:
    print(f"ERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
