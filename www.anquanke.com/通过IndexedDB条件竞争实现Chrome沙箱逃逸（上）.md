> 原文链接: https://www.anquanke.com//post/id/183809 


# 通过IndexedDB条件竞争实现Chrome沙箱逃逸（上）


                                阅读量   
                                **198275**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者bluefrostsecurity，文章来源：labs.bluefrostsecurity.de
                                <br>原文地址：[https://labs.bluefrostsecurity.de/blog/2019/08/08/escaping-the-chrome-sandbox-via-an-indexeddb-race-condition/](https://labs.bluefrostsecurity.de/blog/2019/08/08/escaping-the-chrome-sandbox-via-an-indexeddb-race-condition/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01f46c4d4c0d0af3e3.png)](https://p3.ssl.qhimg.com/t01f46c4d4c0d0af3e3.png)



## 概述

2019年7月30日，谷歌发布Chromium 76.0.3809.87，该版本修复了多个漏洞。 除了列表上的漏洞之外，有一个未公布的漏洞也消失了，这是由于Chrome浏览器的IndexedDB部分重构而造成的。根据修复结果，它改变了在内存中可以跟踪打开数据库的方法。 Chromium使用智能指针替代原始指针，最终修复了漏洞。

在本文中，我们将深入探讨漏洞以及产生的根本原因，并展示如何逃离Chrome沙箱，最终实现利用。 我们用此漏洞作为一个案例，演示如何将向沙盒渲染进程开放的某个IPC接口中的进程间信息泄漏，转变为可以在沙箱外部的浏览器进程中执行任意代码。 最后我会分享出POC代码，利用它可以生成一个反向shell。

虽然本文要讨论的漏洞的Poc代码和Chromium其他漏洞利用代码非常类似，但很多细节是不一样的。我们希望可以为你提供一些参考，帮助你了解如何利用开放的IPC接口中的低级漏洞，最终转变为Google Chrome沙箱逃逸。

下面的分析针对的是Android上的Chromium稳定版，版本号为：75.0.3770.89。



## IndexedDB

IndexedDB API是一个永久性的结构化储存的客户端数据库。Web应用通过它可以在用户浏览器上储存大量数据。数据储存为键值的形式，而值可以是复杂的结构化JavaScript对象。IndexedDB基于事务型数据库模型构建，数据库的每次操作都基于事务的上下文。

Chrome中IndexedDB的具体实现较为复杂，并且向沙盒渲染进程开放了各种IPC接口，这使得它成为寻找Chrome沙箱逃逸漏洞的最佳目标。

### <a class="reference-link" name="Mojo%E6%8E%A5%E5%8F%A3"></a>Mojo接口

Chrome中IndexedDB的大部分是在浏览器进程中实现。 浏览器和渲染中都存在几个不同的mojo IPC接口，用于进程之间的通信，并且使得沙盒渲染能够执行IndexedDB的操作。

IDBFactory mojo接口是渲染的主要入口点。 在一些实用的操作中，它提供了Open方法，在IDBFactory JavaScript接口中对应的是`open()`方法，通过该方法可用于请求打开与数据库的连接。

下面我们将讨论IDBFactory接口提供的两种实用方法`AbortTransactionsAndCompactDatabase`和`AbortTransactionsForDatabase`。 调用其中之一即可中止数据库事务。 有趣的是该版本的渲染器从未使用过这些函数。

在渲染进程中，两个参数通过mojo接口中IDBCallbacks和IDBDatabaseCallbacks的指针传递给Open方法。 前者针对单个请求，被浏览器进程用于返回渲染，后者用于向渲染提示与请求相关的外带事件。

一旦调用Open方法成功后，浏览器就会将指向IDBDatabase接口的指针返回给渲染器。 IDBDatabase接口提供了打开的数据库所有方法。 渲染器使用数据库完毕后，它会调用IDBDatabase接口上的Close方法，用于关闭与浏览器端数据库的连接。

实际上为IndexedDB定义的mojo接口有非常多，我们下面只讨论上面提到的那些。在`third_party/blink/public/mojom/indexeddb/indexeddb.mojom`中你可以看到完整的mojo IndexedDB接口列表。

### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%BA%93%EF%BC%8C%E8%BF%9E%E6%8E%A5%E5%92%8C%E8%AF%B7%E6%B1%82"></a>数据库，连接和请求

IndexedDB有关于数据库和连接的概念。 对于Chrome-IndexedDB，分别由IndexedDBDatabase和IndexedDBConnection类表示。 在某一时间段内可以存在对同一数据库的多个连接，但是每个数据库只有一个IndexedDBDatabase对象。

使用IDBDatabase mojo接口与数据库通信的渲染器将会一直使用该连接来对相应的数据库对象执行操作。

另一个要理解的重要概念是请求。 打开和删除数据库操作不可能同时发生，但会规划执行相应操作的请求。 通过`IndexedDBDatabase::OpenRequest` 和`IndexedDBDatabase::DeleteRequest`类可以实现这些功能。

前面我们提到过，IndexedDB基于事务数据库模型构建。 程序代码将单个事务视为IndexedDBTransaction对象。 大部分操作都是基于事务上下文执行，可以在发生故障时回滚。

### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%BA%93%E6%98%A0%E5%B0%84"></a>数据库映射

程序为了跟踪所有打开的数据库，将通过数据库索引（origin与数据库名构成）映射存储指向相应IndexedDBDatabase对象的原始指针。 数据库映射作为`database_map_`存储在IndexedDBFactoryImpl类中。

当渲染通过调用IDBFactory接口的Open方法请求打开与数据库的连接时，它将查询数据库映射[1]，以确定相应数据库是否开启。

```
void IndexedDBFactoryImpl::Open(
    const base::string16&amp; name,
    std::unique_ptr&lt;IndexedDBPendingConnection&gt; connection,
    const Origin&amp; origin,
    const base::FilePath&amp; data_directory) `{`
  IDB_TRACE("IndexedDBFactoryImpl::Open");
  IndexedDBDatabase::Identifier unique_identifier(origin, name);
  auto it = database_map_.find(unique_identifier);                              [1]
  if (it != database_map_.end()) `{`
    it-&gt;second-&gt;OpenConnection(std::move(connection));                          [2]
    return;
  `}`

[...]

  scoped_refptr&lt;IndexedDBDatabase&gt; database;                                    [3]
  std::tie(database, s) = IndexedDBDatabase::Create(
      name, backing_store.get(), this,
      std::make_unique&lt;IndexedDBMetadataCoding&gt;(), unique_identifier,
      backing_store-&gt;lock_manager());

[...]

  database-&gt;OpenConnection(std::move(connection));
  if (database-&gt;ConnectionCount() &gt; 0) `{`
    database_map_[unique_identifier] = database.get();                          [4]
    origin_dbs_.insert(std::make_pair(origin, database.get()));
  `}`
`}`
```

如果数据库尚未开启，则会创建一个新的IndexedDBDatabase对象[3]，并且将指向该对象的原始指针储存在数据库映射中[4]。

如果数据库已开启，则指向IndexedDBDatabase对象的原始指针从映射中直接提取 [1]，并且用于在IndexedDBDatabase :: OpenConnection方法[2]新建与数据库的连接。

不管是哪种情况，相应数据库对象的IDBDatabase mojo接口指针始终都会返回给渲染器，渲染器可以与相应的数据库连接通信。

### <a class="reference-link" name="IndexedDBDatabase%E5%AF%B9%E8%B1%A1%E7%9A%84%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F"></a>IndexedDBDatabase对象的生命周期

IndexedDBDatabase对象是一种引用计数（Reference counted）的对象。 针对该对象的计数引用被保存在IndexedDBConnection对象，IndexedDBTransaction对象或其他正在进行或待处理的请求对象中。 一旦引用计数降至0，会立即释放对象。

释放数据库对象后，会从数据库映射中删除指向IndexedDBDatabase的相应原始指针，这点非常重要。 当关闭与数据库连接后，会在IndexedDBDatabase::Close方法中出现这种情况。

```
void IndexedDBDatabase::Close(IndexedDBConnection* connection, bool forced) `{`
  DCHECK(connections_.count(connection));
  DCHECK(connection-&gt;IsConnected());
  DCHECK(connection-&gt;database() == this);

  IDB_TRACE("IndexedDBDatabase::Close");

  // Abort outstanding transactions from the closing connection. This can not
  // happen if the close is requested by the connection itself as the
  // front-end defers the close until all transactions are complete, but can
  // occur on process termination or forced close.
  connection-&gt;FinishAllTransactions(IndexedDBDatabaseError(                     [5]
      blink::kWebIDBDatabaseExceptionUnknownError, "Connection is closing."));

  // Abort transactions before removing the connection; aborting may complete
  // an upgrade, and thus allow the next open/delete requests to proceed. The
  // new active_request_ should see the old connection count until explicitly
  // notified below.
  connections_.erase(connection);                                               [6]

  // Notify the active request, which may need to do cleanup or proceed with
  // the operation. This may trigger other work, such as more connections or
  // deletions, so |active_request_| itself may change.
  if (active_request_)                                                          [7]
    active_request_-&gt;OnConnectionClosed(connection);

  // If there are no more connections (current, active, or pending), tell the
  // factory to clean us up.
  if (connections_.empty() &amp;&amp; !active_request_ &amp;&amp; pending_requests_.empty()) `{`  [8]
    backing_store_ = nullptr;
    factory_-&gt;ReleaseDatabase(identifier_, forced);                             [9]
  `}`
`}`
```

Close方法首先会中止目前通信中所有未完成的事务[5]。并且通知它们当前数据库即将关闭[7]。

最后，代码会检查要关闭的连接是否为相应数据库中最后一次连接，是否存在正在执行或即将执行的请求[8]。如果满足上述条件，代码才会通过调用[9]中的IndexedDBFactoryImpl::ReleaseDatabase方法，从数据库映射中删除IndexedDBDatabase的原始指针。

如果不满足条件，原始指针会保存下来。上述代码是在数据库的最后一次连接以及所有的请求都被关闭后，才会从数据库映射中删除原始数据库指针。

Ok，我们假设不满足条件的情况下，存在一个连接或请求仍然引用IndexedDBDatabase对象，使其保持活动状态。 然而在这种情况下存在一些缺陷。



## IndexedDB条件竞争

代码易受条件竞争漏洞的影响，可能导致数据库映射中悬挂的原始指针指向已释放的IndexedDBDarabase对象。

为了创建相应场景，我们首先打开一个数据库，指定版本为0。这会创建一个新的IndexedDB数据库对象并立即打开一个新连接。

之后我们再次发出请求，打开相同数据库，但这次指定版本为2。这将要求数据库执行更新操作。但是由于版本0的连接依旧存在，当OpenRequest执行时更新不能立即启动，直到调用OpenRequest::OnConnectionClosed，所有数据库连接都关闭后。

```
void OnConnectionClosed(IndexedDBConnection* connection) override `{`
  // This connection closed prematurely; signal an error and complete.
  if (connection &amp;&amp; connection-&gt;callbacks() == pending_-&gt;database_callbacks) `{`
    pending_-&gt;callbacks-&gt;OnError(
        IndexedDBDatabaseError(blink::kWebIDBDatabaseExceptionAbortError,
                               "The connection was closed."));
    db_-&gt;RequestComplete(this);
    return;
  `}`

  if (!db_-&gt;connections_.empty())                                             [10]
    return;

  std::vector&lt;ScopesLockManager::ScopeLockRequest&gt; lock_requests = `{`
      `{`kDatabaseRangeLockLevel, GetDatabaseLockRange(db_-&gt;metadata_.id),
       ScopesLockManager::LockType::kExclusive`}``}`;
  db_-&gt;lock_manager_-&gt;AcquireLocks(
      std::move(lock_requests),
      base::BindOnce(&amp;IndexedDBDatabase::OpenRequest::StartUpgrade,
                     weak_factory_.GetWeakPtr()));
`}`
```

打开第二个数据库连接后，IndexedDBDatabase::active**request**将指向版本2的OpenRequest对象，并且这个对象会延迟数据库的更新操作。

如果我们关闭第一个数据库连接（版本0），IndexedDBDatabase::Close会删除与数据库的最后一个连接[6]，然后在IndexedDBDatabase::active**request**指向的OpenRequest上调用OpenRequest::OnConnectionClosed。

因为已经删除与数据库的最后一次连接，OpenRequest::OnConnectionClosed将通过调用IndexedDBDatabase: OpenRequest::StartUpgrade启动延迟更新。 StartUpgrade将创建一个新连接并在当前事务中安排新的VersionChangeOperation任务：

```
// Initiate the upgrade. The bulk of the work actually happens in
// IndexedDBDatabase::VersionChangeOperation in order to kick the
// transaction into the correct state.
void StartUpgrade(std::vector locks) `{`
  connection_ = db_-&gt;CreateConnection(pending_-&gt;database_callbacks,
                                      pending_-&gt;child_process_id);
  DCHECK_EQ(db_-&gt;connections_.count(connection_.get()), 1UL);

  std::vector&lt;int64_t&gt; object_store_ids;

  IndexedDBTransaction* transaction = connection_-&gt;CreateTransaction(
      pending_-&gt;transaction_id,
      std::set&lt;int64_t&gt;(object_store_ids.begin(), object_store_ids.end()),
      blink::mojom::IDBTransactionMode::VersionChange,
      new IndexedDBBackingStore::Transaction(db_-&gt;backing_store()));
  transaction-&gt;ScheduleTask(
      base::BindOnce(&amp;IndexedDBDatabase::VersionChangeOperation, db_,
                     pending_-&gt;version, pending_-&gt;callbacks));
  transaction-&gt;Start(std::move(locks));
`}`
```

如果我们返回到方法IndexedDBDatabase::Close 的检查[8]，将不满足条件。因为仍然存在与数据库的连接，所以不会删除指向当前IndexedDBDatabase对象的原始指针。

调用mojo Close方法关闭与数据库的连接（版本0）后，我们立即从渲染中调用IDBFactory mojo接口上的AbortTransactionsForDatabase方法，这样我们就有机会在IndexedDBDatabase::VersionChangeOperation任务发布之前执行。

调用AbortTransactionsForDatabase mojo方法后，会在与数据库的所有连接上调用IndexedDBConnection::FinishAllTransactions方法：

```
void IndexedDBConnection::FinishAllTransactions(
    const IndexedDBDatabaseError&amp; error) `{`
  DCHECK_CALLED_ON_VALID_SEQUENCE(sequence_checker_);
  std::unordered_map&lt;int64_t, std::unique_ptr&lt;IndexedDBTransaction&gt;&gt; temp_map;
  std::swap(temp_map, transactions_);
  for (const auto&amp; pair : temp_map) `{`
    auto&amp; transaction = pair.second;
    if (transaction-&gt;is_commit_pending()) `{`
      IDB_TRACE1("IndexedDBDatabase::Commit", "transaction.id",
                 transaction-&gt;id());
      transaction-&gt;ForcePendingCommit();
    `}` else `{`
      IDB_TRACE1("IndexedDBDatabase::Abort(error)", "transaction.id",
                 transaction-&gt;id());
      transaction-&gt;Abort(error);
    `}`
  `}`
`}`
```

由于没有其他（方法）提交，代码会在所有事务上调用IndexedDBTransaction::Abort方法，最终调用IndexedDBDatabase :: TransactionFinished [11]，表示事务已完成。

```
void IndexedDBTransaction::Abort(const IndexedDBDatabaseError&amp; error) `{`

[...]

  database_-&gt;TransactionFinished(mode_, false);                             [11]

  // RemoveTransaction will delete |this|.
  // Note: During force-close situations, the connection can be destroyed during
  // the |IndexedDBDatabase::TransactionFinished| call
  if (connection_)
    connection_-&gt;RemoveTransaction(id_);
`}`
```

IndexedDBDatabase::TransactionFinished调用OpenRequest::UpgradeTransactionFinished，然后调用IndexedDBDatabase::RequestComplete以完成请求，并删除[12]处的IndexedDBDatabase::active**request**指针：

```
void IndexedDBDatabase::RequestComplete(ConnectionRequest* request) `{`
  DCHECK_EQ(request, active_request_.get());
  scoped_refptr&lt;IndexedDBDatabase&gt; protect(this);
  active_request_.reset();                                                  [12]

  // Exit early if |active_request_| held the last reference to |this|.
  if (protect-&gt;HasOneRef())
    return;

  if (!pending_requests_.empty())
    ProcessRequestQueue();
`}`
```

每个OpenRequest对象都有相应的IndexedDBConnection对象。 通过删除IndexedDBDatabase::active**request**指针清理活跃的OpenRequest时，会释放IndexedDBConnection对象，包括其所有事务。

此时，对IndexedDBDatabase对象的所有引用都消失并且将被释放。 同时，我们关闭了与数据库的所有连接，但绕过代码，无需从数据库映射中删除原始的IndexedDBDatabase指针。Ok，现在我们创建了这样一个场景，数据库映射中有一个悬挂的原始指针，并且该指针指向已释放的IndexedDBDatabase对象！

如果我们从渲染器打开同一数据库，那么可以对已释放的IndexedDBDatabase对象做一些操作。


