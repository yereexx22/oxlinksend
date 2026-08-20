import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables desde el archivo .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Debes configurar las variables de entorno SUPABASE_URL y SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)