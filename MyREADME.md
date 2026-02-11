1. 云上换api或者换模型
cd chatgpt-on-wechat
nano docker-compose.yml
sudo docker compose up -d

2. 查看实时日志
cd chatgpt-on-wechat
sudo docker logs -f chatgpt-on-wechat
退出查看 按键盘 Ctrl + C

3. 代码更新
cd chatgpt-on-wechat
git pull
sudo docker-compose up -d --build

4. 关机维护
cd chatgpt-on-wechat
sudo docker compose down

5. 服务器重启后（开机启动）
cd chatgpt-on-wechat
sudo docker compose up -d

6. 容器是否alive
sudo docker ps

7. 访问SQLite
SQLite 策略改为允许
cd chatgpt-on-wechat
./scripts/start_db_web.sh
不要关闭命令行
访问http://xxxxxxxx:9898