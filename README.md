# CFD 自动化平台

## 1. 部署

### 1. 安装软件

软件清单

```bash
1. python 3.10
2. redis
3. mysql
```

### 2. 安装python包

`pip install -r requirements.txt`

### 3. 数据库建表

```bash
cd server
aerich init -t dbs.database.TORTOISE_ORM
aerich init-db
```

### 4. 入库`FluentProf`和`Admin`表

```bash
cd server
python scripts/add.py
```

### 4. 启动服务

#### 1. 启动fastapi

```bash
cd server
python main.py
```

#### 2. 启动celery

`bash start.sh` 或者

```bash
cd server
celery -A worker.celery worker -l info -c 10
```

