import psycopg2

DATABASE_URL = "postgresql://tigerengage_i80s_user:3ByTjcPKJW0B9ZGBOUPUqR6tAvE9XNJT@dpg-cqglsjij1k6c73dg22b0-a.ohio-postgres.render.com/tigerengage_i80s"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
