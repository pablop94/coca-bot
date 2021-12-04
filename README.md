# La Coca

La coca es un bot que nace para recordarnos a un grupo de amigues quienes tienen que hacer las compras para las juntadas.

## Modo de uso
```
/agregar [nombre] [comida] 
```
Con este comando agregamos una comida a la lista. Se enviará un recordatorio los días `REMINDER_DAYS` a las `REMINDER_HOUR_UTC` en punto, teniendo en cuenta el orden en el que fueron ingresadas.

```
/historial
```
Con este comando vemos un contador histórico de quienes se encargaron de las comidas.

## Variables de ambiente
- `CHAT_ID` el chat donde se enviará el recordatorio.
- `DEVELOPER_CHAT_ID` el chat donde se enviarán errores en caso de haberlos.
- `TELEGRAM_TOKEN` el token del bot de Telegram.
- `REDIS_URL` la url de la base de datos de redis.
- `REMINDER_HOUR_UTC` la hora a la que se envía el recordatorio en UTC.
- `REMINDER_DAYS` los días en que se envía el recordatorio, 0 es lunes, 6 es domingo separado por coma. Por ejemplo 2,3 lo envía miercoles y jueves.

## Ejecución
### Bot
```
python -m src.coca
```

### Tests
```
python -m unittest
```