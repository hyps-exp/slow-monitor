# slow-monitor
slow-monitor using Influxdb2, Telegraf, Grafana...

# Environment

- Almalinux 9.4
- Influxdb 2.7.10
- Telegraf 1.32.2
- Grafana 11.3.0

使用するPC。
| | |
| --- | --- |
| OS | Almalinux release 9.4 (Seafoam Ocelot) |
| CPU | AMD Ryzen 5 8600G w/ Radeon 760M Graphics |
| Memory | 16 GB CT16G48C40U5.C8A1 x 2 |
| Hostname | db-hyps.rcnp.osaka-u.ac.jp |
| IP Address | 172.16.205.212 |

# Install

## Influxdb2

### InfluxDBリポジトリの追加

```bash
sudo tee /etc/yum.repos.d/influxdata.repo <<EOF
[influxdata]
name=InfluxData Repository - RHEL \$releasever
baseurl=https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://repos.influxdata.com/influxdb.key
EOF
```

### InfluxDBのインストール

```bash
sudo dnf install influxdb2 influxdb2-cli
```

### InfluxDBサービスの起動と自動起動設定

```bash
sudo systemctl enable --now influxdb
```

### ファイアウォールの設定（必要な場合）

InfluxDBのデフォルトポート8086を許可。

```bash
sudo firewall-cmd --add-port=8086/tcp --permanent
sudo firewall-cmd --reload
```

### InfluxDBの初期設定

インストール後、初めてのアクセス時に初期設定を行う必要がある。Webブラウザで http://localhost:8086 にアクセスして、以下の設定を行う。

- 初期ユーザー: 管理者ユーザー名とパスワード
- 初期組織名: データ管理用の組織名
- 初期バケット: データを格納するバケット（データベースのようなもの）

組織名とバケットは短い名前推奨。

### 動作確認

初期設定が完了すると、InfluxDBのCLIやAPIでデータの読み書きができる。
例えば、組織やバケットの情報を確認するには、次のようなコマンドを実行。

```bash
influx org list
influx bucket list
```
