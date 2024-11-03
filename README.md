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

## InfluxDB 2

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

### データ保存場所

`/etc/influxdb/config.toml`で、データ保存場所を変更可能。
```toml
bolt-path = "/custom/path/influxdb2/influxd.bolt"
engine-path = "/custom/path/influxdb2/engine"
```

## Telegraf

### Telegrafのインストール

```bash
sudo dnf install telegraf
```

### Telegrafの設定

TelegrafをInfluxDB 2.xと接続するためのtelegraf.confの設定例を以下に示す。
ここでは、InfluxDB 2.xにデータを送信するためのoutputs.influxdb_v2プラグインと、システムの基本的なメトリクス（CPU、メモリなど）を収集する設定を含む。

```toml
[global_tags]
  environment = "production"

[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = ""
  debug = false
  quiet = false
  logfile = ""

# CPU メトリクスの収集
[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = false

# メモリ メトリクスの収集
[[inputs.mem]]

# InfluxDB 2.x 出力プラグイン
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "YOUR_INFLUXDB_TOKEN"
  organization = "YOUR_ORG_NAME"
  bucket = "YOUR_BUCKET_NAME"
  timeout = "5s"
```

設定ファイルの各項目について
- urls: InfluxDB 2.xのURL。デフォルトはhttp://localhost:8086だが、リモートサーバの場合はホスト名やIPアドレスを指定。
- token: InfluxDB 2.xの認証トークンです。Web UIから発行。
- organization: InfluxDB 2.xの組織名。
- bucket: データを保存するバケット名。Web UIでバケットを作成しておく必要がある。
設定ファイルを保存したら、Telegrafを起動して設定を反映させる。

```bash
sudo systemctl enable --now telegraf
```

## Grafana

### Grafanaリポジトリの追加
Grafanaの公式リポジトリを/etc/yum.repos.d/grafana.repoに追加。

```bash
sudo tee /etc/yum.repos.d/grafana.repo <<EOF
[grafana]
name=Grafana Repository
baseurl=https://rpm.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
EOF
```

### Grafanaのインストール

```bash
sudo dnf install grafana
```

### Grafanaサービスの起動と自動起動設定

```bash
sudo systemctl enable --now grafana-server
```
### ファイアウォールの設定（必要な場合）

AlmaLinuxのファイアウォールが有効な場合、Grafanaのデフォルトポート3000を許可。

```bash
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload
```

### WebブラウザからGrafanaにアクセス
インストールとサービスの起動が完了したら、Webブラウザで以下のURLにアクセスして、GrafanaのWebインターフェースを開く。

```arduino
http://YOUR_SERVER_IP:3000
```

### 初期ログイン情報
初回ログインのデフォルトのユーザー名とパスワードは

- ユーザー名: admin
- パスワード: admin

ログイン後、パスワードの変更が求められるので、新しいパスワードを設定する。
