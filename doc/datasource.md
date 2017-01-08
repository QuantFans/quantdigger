# 数据源配置

QuantDigger目前支持CSV、MongoDB、SQLite和TuShare数据源，并支持自定义数据源。QuantDigger通过配置中的`source`项来指定程序运行时使用的数据源，默认使用CSV数据源。可以通过`ConfigUtil.set`方法修改数据源，例如：

```Python
ConfigUtil.set(source='csv', data_path= './data')
```

指定了读取`./data`文件夹下的CSV文件作为数据源。

## 数据源的几个要素

* *contracts数据*：

|          域          |  类型  |     描述     |
|:--------------------:|:------:|:------------:|
|        `code`        | 字符串 |   合约代码   |
|      `exchange`      | 字符串 |    交易所    |
|        `name`        | 字符串 |   合约名称   |
|        `spell`       | 字符串 |     拼音     |
|  `long_margin_ratio` | 浮点数 |  多头保证金  |
| `short_margin_ratio` | 浮点数 |  空头保证金  |
| `price_tick`         | 浮点数 | 最小变动价位 |
| `volume_multiple`    | 浮点数 | 合约乘数     |

* *一个合约要素*：周期、交易所、合约代码

## CSV数据源

### 配置

* `source='csv'`
* `data_path`：数据源所在的路径

### 存储格式

所有合约数据存储在`data_path`路径指定的文件夹中，通过如下目录结构表示合约的属性：

```{data_path}/{周期}/{交易所}/{合约代码}.csv```

例如周期一天，交易所SHFE，合约代码BB的数据存储在文件`{data_path}/1DAY/SHFE/BB.csv`中。
CSV文件结构为：

|     域     |  类型  |                 描述                |
|:----------:|:------:|:-----------------------------------:|
| `datetime` | 字符串 | `'yyyy-MM-dd HH:mm:ss'`格式的时间戳 |
|   `open`   | 浮点数 |                开盘价               |
|   `close`  | 浮点数 |                收盘价               |
|   `high`   | 浮点数 |                最高价               |
|    `low`   | 浮点数 |                最低价               |
|  `volume`  | 浮点数 |                成交量               |

contracts数据存储在文件`{data_path}/CONTRACTS.csv中

## MongoDB数据源

### 配置

* `source='mongodb'`
* `address`：MongoDB地址
* `port`：MongoDB端口
* `dbname`：MongoDB库名

### 存储格式

所有合约数据存储在`dbname`指定的数据库中。集合`contract`存储所有合约的基本信息。特定合约存储在命名为如下格式的集合中：

```
{周期}.{交易所}.{合约代码}
```

例如周期一天，交易所SHFE，合约代码BB的数据存储在集合`1DAY.SHFE.BB`中。
保存合约数据的集合结构为：

|     域     |  类型  |                            描述                            |
|:----------:|:------:|:----------------------------------------------------------:|
|    `id`    | 整型数 | 使用周期与时间戳根据`dateutil.encode2id`函数编码的13位整数 |
| `datetime` |  日期  |                           时间戳                           |
|   `open`   | 浮点数 |                           开盘价                           |
|   `close`  | 浮点数 |                           收盘价                           |
|   `high`   | 浮点数 |                           最高价                           |
|    `low`   | 浮点数 |                           最低价                           |
|  `volume`  | 浮点数 |                           成交量                           |

contracts数据存储在集合`contract`中

## SQLite数据源

### 配置

* `source='sqlite'`
* `data_path`：SQLite文件路径

### 存储格式

表`contract`存储所有合约的基本信息。特定合约存储在命名为如下格式的集合中：

```
{交易所}_{合约代码}
```

例如周期一天，交易所SHFE，合约代码BB的数据存储在表`SHFE_BB`中。
保存合约数据的表结构为：

|     字段    |  类型  |                            描述                            |
|:----------:|:------:|:----------------------------------------------------------:|
|    `id`    | 整型数 | 使用周期与时间戳根据`dateutil.encode2id`函数编码的16位整数 |
| `datetime` |  日期  |                           时间戳                           |
|   `open`   | 浮点数 |                           开盘价                           |
|   `close`  | 浮点数 |                           收盘价                           |
|   `high`   | 浮点数 |                           最高价                           |
|    `low`   | 浮点数 |                           最低价                           |
|  `volume`  | 浮点数 |                           成交量                           |

contracts数据存储在表`contract`中

## TuShare数据源

### 配置

* `source='tushare'`

### 带缓存的TuShare数据源

使用TuShare数据源每次取数据时都必须从TuShare服务器下载数据。为了改善效率，可使用带缓存的TuShare数据源，该数据源会将已访问过的数据缓存在本地文件中。配置如下：

* `source='cached-tushare'`
* `cache_path`：缓存存放的路径

## 自定义数据源

TODO

------

## 工具方法

`datautil`

`import_data(fpaths, ds)`
