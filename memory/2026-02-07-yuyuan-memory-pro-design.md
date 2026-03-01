---
name: yuyuan-memory-pro
description: |
  芋圆生产级记忆系统 - 最终版设计文档
  核心策略：Kimi 2.5 极速对话，GLM-4.7 后台慢速整理（5分钟容忍，免费额度无限用）
  目标：上下文永不过载，记忆零丢失，主线程零等待

# 触发器：三层防护（主动+被动+手动）
triggers:
  # 1. 每小时预防性整理（最重要）
  - type: cron
    schedule: "0 * * * *"
    action: hourly_preemptive_compaction
    priority: critical
    
  # 2. 上下文监控（保守阈值，给 GLM-4.7 留时间）
  - type: metric
    metric: "context_token_ratio"
    threshold: 0.60          # 60% 触发，早于官方 75%
    action: emergency_flush
    debounce: "10m"          # 10分钟防抖，避免 GLM-4.7 慢导致频繁触发
    
  # 3. 拦截官方 compaction（用我们的智能分类替代）
  - type: event
    event: "pre_compaction_flush"
    action: smart_classification
    intercept: true
    
  # 4. 手动触发
  - type: command
    patterns: ["/compact", "总结现在", "保存记忆", "存档"]
    action: full_checkpoint

# 异构模型配置：主快从慢，成本分离
compute:
  primary:
    model: "kimi-k2.5"
    reserved_for: ["user_dialogue", "critical_decisions", "emergency_flush"]
    
  background:
    model: "glm-4.7"
    assigned_tasks: ["memory_summarization", "pattern_extraction", "vector_indexing"]
    max_concurrent: 1        # GLM-4.7 极慢，单实例串行，避免堆积
    
    # 关键：超时和重试配置（针对智谱免费额度优化）
    timeout: "300s"          # 5分钟豪华超时
    retry_policy:
      max_attempts: 1        # 只重试1次！首次失败+1次重试=共2次机会
      backoff: "fixed"       # 固定30秒后立即重试
      fast_abort:
        first_attempt_threshold: "240s"  # 首次超过4分钟直接放弃，立即回退
        
    fallback_to: "kimi-k2.5" # 2次失败后立即回退（总耗时最多6分钟）
    
  embedding:
    provider: "local"        # 本地 embedding，零成本
    model: "builtin"
    fallback: "none"         # 失败时用关键词搜索，不花钱

# 三层记忆架构（带详细优先级）
memory_tiers:
  # Tier 1: 热记忆（当前 Session，永不丢失关键上下文）
  hot:
    storage: "memory/hot_session.md"
    retention: "current_session_only"
    max_tokens: 6000         # 给热记忆充足空间
    
    # 保留优先级矩阵（P0 最高，P4 最低）
    content_priority:
      P0:                    # 永不淘汰（除非用户明确清除）
        type: "active_code_context"
        description: "正在调试的代码、断点状态、未完成函数"
        persist_until: "explicit_delete"
        
      P1:                    # 用户显式标记
        type: "user_explicit_hold"
        description: "用户说'记住这个'、'等一下'、'保留上下文'"
        persist_until: "user_release"
        
      P2:                    # 活跃任务栈
        type: "unfinished_tasks"
        description: "进行中的任务及进度"
        persist_until: "task_complete_or_1h_stale"
        
      P3:                    # 最近事实（关键调整：1小时）
        type: "recent_facts"
        description: "最近 1 小时内的事实（原30分钟延长至1小时）"
        persist_until: "age_>1h_then_decay"
        
      P4:                    # 临时问题
        type: "pending_questions"
        description: "待回答的问题"
        persist_until: "answered_or_30m"
        
    eviction_policy: "lru_preserve_p0_p1"  # LRU 淘汰，但 P0-P1 永不被淘汰
    sync_strategy: "realtime"
    load_policy: "always_inject"

  # Tier 2: 温记忆（每日详细日志，7天保留）
  warm:
    storage: "memory/{{YYYY-MM-DD}}.md"
    retention: "7_days"
    content_types:
      - error_patterns:      # 最高保留权重
          weight: 1.5
          retention: "full_detail"
      - successful_patterns:
          weight: 1.2
          retention: "conclusion_only"
      - code_evolution:
          weight: 1.0
          retention: "diff_summary"
      - exploration_logs:
          weight: 0.7
          retention: "compressed_summary"
    sync_strategy: "hourly_batch"
    load_policy: "on_demand_search"

  # Tier 3: 冷记忆（永久精炼知识）
  cold:
    storage: "MEMORY.md"
    retention: "permanent"
    admission_criteria:      # 准入门槛（必须满足至少一条）
      - "user_explicit_remember"
      - "error_pattern_repeated_2x"
      - "architectural_decision"
      - "user_correction"
      - "complex_problem_solved_>10m"
    min_confidence: 0.8      # GLM-4.7 置信度必须 >0.8
    sync_strategy: "daily_merge"
    load_policy: "session_start_inject"

# 核心工作流
actions:
  # Action 1: 每小时预防性压缩（GLM-4.7 后台执行，5分钟容忍）
  hourly_preemptive_compaction:
    model: "glm-4.7"
    async: true              # 必须异步！不阻塞用户对话
    timeout: "300s"          # 5分钟超时
    retry: 1                 # 只重试1次
    
    steps:
      - name: extract_hot_facts
        prompt: |
          分析最近 1 小时的对话，提取热事实（按 P0-P4 优先级分类）：
          
          P0 (Active Code): 正在编辑的代码、调试状态、断点
          P1 (Explicit Hold): 用户说"记住"、"等一下"的内容
          P2 (Tasks): 未完成的任务栈及进度
          P3 (Recent Facts): 最近 1 小时的关键信息（用户身份、当前目标等）
          P4 (Questions): 待回答的问题
          
          输出严格 JSON: {"p0": [...], "p1": [...], "p2": [...], "p3": [...], "p4": [...]}
        output_format: "json"
        max_tokens: 4000
        
      - name: update_hot_buffer
        tool: "context_inject"
        target: "hot_session.md"
        format: |
          # Hot Buffer {{timestamp}}
          ## P0 (Code Context)
          {{p0}}
          ## P1 (Explicit Holds)
          {{p1}}
          ## P2 (Active Tasks)
          {{p2}}
          ## P3 (Recent Facts - 1h)
          {{p3}}
          ## P4 (Pending)
          {{p4}}

      - name: generate_warm_summary
        prompt: |
          将过去 1 小时对话压缩为结构化 Markdown：
          ### {{hour}}:00 Summary
          - **Decisions**: 关键决策
          - **Errors**: 错误及修复（高优先级）
          - **Code**: 代码变更摘要
          - **Context**: 重要背景
        append_to: "memory/{{today}}.md"

      - name: truncate_context
        tool: "compaction"
        strategy: "preserve_hot_only"
        reclaim_target: "50%"  # 激进释放 50%，确保 Kimi 轻快

  # Action 2: 智能分类到 Cold 记忆（GLM-4.7 慢速执行）
  smart_classification:
    model: "glm-4.7"
    async: true
    timeout: "300s"
    trigger: "pre_compaction_flush"
    
    steps:
      - name: classify_for_cold
        prompt: |
          判断哪些内容值得永久保存 (MEMORY.md)：
          标准：1)用户明确说记住 2)错误重复2次+ 3)架构决策 4)用户纠正 5)复杂问题解决
          
          输出 JSON: {"durable": [{"content": "...", "confidence": 0.9, "type": "..."}]}
        min_confidence: 0.8
        
      - name: atomic_append_cold
        tool: "memory_append"
        target: "MEMORY.md"
        deduplicate: true
        
      - name: reindex_vectors
        tool: "memory_reindex"
        background: true

  # Action 3: 模式提取（每4小时，GLM-4.7 深度思考）
  pattern_extraction:
    model: "glm-4.7"
    async: true
    timeout: "300s"
    schedule: "0 */4 * * *"
    
    steps:
      - name: extract_patterns
        prompt: |
          分析过去4小时的错误/成功，提取"如果...就..."决策规则。
          输出到 patterns/{{date}}.md，并更新 Thinking Model。
        output_to: "memory/patterns/{{date}}.md"

  # Action 4: 紧急刷新（Kimi 2.5 极速执行）
  emergency_flush:
    model: "kimi-k2.5"       # 主模型极速处理
    sync: true                # 同步执行，立即响应
    timeout: "10s"           # 10秒必须完成
    
    steps:
      - name: critical_preserve
        prompt: |
          上下文 60%！立即提取：
          1. 未完成代码（文件名+行号）
          2. 用户明确待办
          3. 当前调试状态
        max_tokens: 800
        
      - name: aggressive_truncate
        tool: "compaction"
        strategy: "emergency"
        preserve_only: ["p0", "p1", "last_3_turns"]

# 监控与告警（针对 GLM-4.7 慢速）
monitoring:
  - metric: "glm47_task_duration"
    threshold: "240s"        # 超过4分钟告警
    action: "log_warning"
    
  - metric: "glm47_queue_depth"
    threshold: 2             # 堆积2个任务即告警
    action: "notify_user: 后台整理堆积，记忆可能延迟"
    
  - metric: "fallback_rate"
    threshold: 0.1           # 回退率超过10%告警
    action: "alert: GLM-4.7 不稳定，检查智谱服务"

# 成本保护（利用智谱免费额度）
cost_control:
  background_budget:
    monthly_limit: "1000000000"  # 10亿 token（智谱会员）
    alert_at: "80%"
    
  primary_protection:
    max_background_cpu: 20%      # GLM-4.7 最多占 20% CPU
    yield_to_primary: true        # Kimi 2.5 优先

# 元数据
metadata:
  openclaw:
    version: "1.0.0"
    min_version: "0.9.0"
    requires: ["memory-core"]
    emoji: "🧠"
    primaryEnv: "yuyuan"
    notes: "GLM-4.7 极慢但免费，5分钟容忍，1次重试，快速回退 Kimi 2.5"
---
