import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio.engine import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from config import db_config

Base = declarative_base()
metadata = Base.metadata


class aobject(object):
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass


class Database(aobject):
    _instance: 'Database' = None

    async def __init__(self) -> None:
        self._config = db_config
        self.engine: AsyncEngine = create_async_engine(self.prepare_connection_string(self._config), #poolclass=NullPool,
                                                       echo=False, convert_unicode=True, encoding='utf-8')
        self.connection = await self.engine.connect()
        self.metadata = metadata
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

    async def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = await super(Database, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    async def get_class_session(cls) -> AsyncSession:
        return (await cls()).get_session()

    def get_session(self) -> AsyncSession:
        return sqlalchemy.orm.sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)()

    @staticmethod
    def prepare_connection_string(config: dict):
        """
        Prepares the connection string for the database.
        :param config: The config dictionary.
        :return: The connection string.
        """
        user = config.pop('user') or ''
        password = config.pop('password') or ''
        host = config.pop('host')
        port = config.pop('port') or ''
        database = config.pop('database') or ''
        engine = config.pop('engine')
        return (f'{engine}://{user}{":" if user and password else ""}'
                f'{password}{"@" if user and password else ""}{host}{":" if port else ""}{port}'
                f'{"/" if database else ""}{database}{"?" if config else ""}'
                f'{"&".join(f"{key}={value}" for key, value in config.items())}')
