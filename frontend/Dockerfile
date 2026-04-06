FROM node:20-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM alpine:latest
WORKDIR /var/html/frontend
COPY --from=build-stage /app/dist .
CMD ["sh", "-c", "cp -rn . /var/html/frontend/ && tail -f /dev/null"]