import { Database, open } from 'sqlite';
import sqlite3 from 'sqlite3';
import path from 'path';

let db: Database | null = null;

export async function getDatabase(): Promise<Database> {
  if (db) {
    return db;
  }

  // 데이터베이스 파일 경로 설정
  const dbPath = path.join(process.cwd(), 'users.db');
  
  db = await open({
    filename: dbPath,
    driver: sqlite3.Database
  });

  // 사용자 테이블 생성
  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  return db;
}

export async function closeDatabase() {
  if (db) {
    await db.close();
    db = null;
  }
}
