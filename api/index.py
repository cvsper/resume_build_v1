import sys
sys.path.append('..')

from app import app as application

# Vercel Python handler
# Expose as 'app' for @vercel/python
app = application
