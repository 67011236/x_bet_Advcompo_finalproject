import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host='xbet_db',
        port='5432',
        database='xbet_db',
        user='xbet_user',
        password='xbet_pass'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'game1'
        )
    """)
    table_exists = cursor.fetchone()[0]

    if table_exists:
        print('✅ Table game1 exists')
        # Check columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'game1' 
            AND table_schema = 'public'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f'📋 Columns: {columns}')
        
        # Add missing columns if needed
        required = ['user_id', 'bet_amount', 'selected_color', 'result_color', 'won', 'payout_amount', 'played_at']
        missing = [col for col in required if col not in columns]
        
        if missing:
            print(f'🔧 Adding missing columns: {missing}')
            column_defs = {
                'user_id': 'TEXT NOT NULL DEFAULT \'\'',
                'bet_amount': 'INTEGER NOT NULL DEFAULT 0',
                'selected_color': 'TEXT NOT NULL DEFAULT \'blue\' CHECK (selected_color IN (\'blue\',\'white\'))',
                'result_color': 'TEXT NOT NULL DEFAULT \'blue\' CHECK (result_color IN (\'blue\',\'white\'))',
                'won': 'INTEGER NOT NULL DEFAULT 0 CHECK (won IN (0,1))',
                'payout_amount': 'INTEGER NOT NULL DEFAULT 0',
                'played_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col in missing:
                if col in column_defs:
                    try:
                        cursor.execute(f'ALTER TABLE game1 ADD COLUMN {col} {column_defs[col]}')
                        print(f'  ✅ Added: {col}')
                    except Exception as e:
                        print(f'  ❌ Failed {col}: {e}')
        else:
            print('✅ All columns exist')
    else:
        print('🔨 Creating table game1...')
        cursor.execute("""
            CREATE TABLE game1 (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                bet_amount INTEGER NOT NULL CHECK (bet_amount > 0),
                selected_color TEXT NOT NULL CHECK (selected_color IN ('blue','white')),
                result_color TEXT NOT NULL CHECK (result_color IN ('blue','white')),
                won INTEGER NOT NULL CHECK (won IN (0,1)),
                payout_amount INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute('CREATE INDEX idx_game1_user_id ON game1(user_id)')
        cursor.execute('CREATE INDEX idx_game1_played_at ON game1(played_at)')
        print('✅ Table created successfully!')

    cursor.execute('SELECT COUNT(*) FROM game1')
    count = cursor.fetchone()[0]
    print(f'📊 Current records: {count}')

    conn.close()
    print('🎯 Database setup complete!')

except Exception as e:
    print(f'❌ Error: {e}')