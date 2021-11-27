# La Coca

La coca es un bot que nace para recordarnos a un grupo de amigos quienes tienen que hacer las compras para las juntadas.

## Modo de uso
```
/agregar [nombre] [comida] 
```
Con este comando agregamos una comida a la lista. Se enviará un recordatorio cada jueves a las 12 teniendo en cuenta el orden en el que fueron ingresadas.

## Variables de ambiente
- `CHAT_ID` el chat donde se enviará el recordatorio.
- `DEVELOPER_CHAT_ID` el chat donde se enviarán errores en caso de haberlos.
- `TELEGRAM_TOKEN` el token del bot de Telegram.
- `REDIS_URL` la url de la base de datos de redis.

## Ejecución
### Bot
```
python -m src.coca
```

### Tests
```
python -m unittest
```