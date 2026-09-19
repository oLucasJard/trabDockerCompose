#!/bin/sh
set -e

echo "Aguardando o PostgreSQL em $POSTGRES_HOST:$POSTGRES_PORT..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "Banco disponivel."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

