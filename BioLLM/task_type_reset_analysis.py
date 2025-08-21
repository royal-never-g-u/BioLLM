#!/usr/bin/env python3
"""
分析task_type被重置的所有情况
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def analyze_task_type_reset_scenarios():
    """分析task_type被重置的所有情况"""
    print("🔍 分析task_type被重置的所有情况")
    print("=" * 80)
    
    print("\n📋 1. 系统初始化时重置")
    print("   位置: bio_task.py -> initialize_task_file()")
    print("   触发条件:")
    print("   - 项目启动时调用 initialize_bio_task()")
    print("   - 手动调用 clear_task()")
    print("   重置行为: 创建空的BioTask对象，task_type = ''")
    print("   影响: 清空所有字段，包括task_type")
    print("   ⚠️  这是唯一会完全重置task_type的地方")
    
    print("\n📋 2. 实验执行过程中的状态更新")
    print("   位置: experiment_executor.py -> execute_gene_deletion()")
    print("   触发条件:")
    print("   - 开始执行基因删除分析时")
    print("   - 分析完成时")
    print("   - 分析出错时")
    print("   重置行为:")
    print("   - task_type='gene_deletion_analysis_running' (开始)")
    print("   - task_type='gene_deletion_analysis_completed' (完成)")
    print("   - task_type='gene_deletion_analysis_error' (错误)")
    print("   影响: 覆盖现有的task_type，但这是临时的执行状态")
    
    print("\n📋 3. 用户确认实验时重置")
    print("   位置: app.py -> 用户响应实验提示")
    print("   触发条件:")
    print("   - 用户对'Do you want to use this model for experiments?'回答'yes'")
    print("   重置行为: task_type='experiment'")
    print("   影响: 覆盖现有的task_type")
    
    print("\n📋 4. TaskPickAgent智能更新")
    print("   位置: agent/task_pick_agent.py -> analyze_user_input()")
    print("   触发条件:")
    print("   - 用户输入匹配到预定义的分析类型")
    print("   重置行为: 更新为匹配的分析类型ID (1-6)")
    print("   影响: 智能更新，不匹配时保持原值")
    print("   ✅ 这是期望的行为，不是真正的'重置'")
    
    print("\n📋 5. 手动更新")
    print("   位置: 各种测试脚本和示例代码")
    print("   触发条件:")
    print("   - 测试脚本中的 update_current_task(task_type=X)")
    print("   - 示例代码中的手动设置")
    print("   重置行为: 根据传入的值更新")
    print("   影响: 有意的更新操作")
    
    print("\n📋 6. 文件损坏或读取失败")
    print("   位置: bio_task.py -> load_task()")
    print("   触发条件:")
    print("   - bio_task.json文件损坏")
    print("   - 文件读取权限问题")
    print("   - JSON格式错误")
    print("   重置行为: 返回None，下次更新时创建新的BioTask对象")
    print("   影响: 间接导致重置")
    
    print("\n" + "=" * 80)
    print("🎯 总结：task_type被重置的情况")
    print("=" * 80)
    
    print("\n🚨 会完全重置task_type的情况:")
    print("   1. 系统初始化 (initialize_bio_task)")
    print("   2. 手动清空 (clear_task)")
    print("   3. 文件损坏或读取失败")
    
    print("\n⚠️  会覆盖task_type的情况:")
    print("   1. 实验执行状态更新 (临时状态)")
    print("   2. 用户确认实验 (task_type='experiment')")
    print("   3. TaskPickAgent识别到匹配类型 (智能更新)")
    print("   4. 手动更新操作")
    
    print("\n✅ 不会重置task_type的情况:")
    print("   1. TaskPickAgent未识别到匹配类型 (保持原值)")
    print("   2. 正常的命令处理流程")
    print("   3. 用户输入不相关的文本")
    
    print("\n💡 建议:")
    print("   1. 避免频繁调用initialize_bio_task()")
    print("   2. 实验完成后恢复之前的task_type")
    print("   3. 定期备份bio_task.json文件")
    print("   4. 监控文件完整性")

def check_current_task_type_status():
    """检查当前task_type状态"""
    print("\n🔍 检查当前task_type状态")
    print("-" * 40)
    
    try:
        from bio_task import get_current_task
        from analysis_types import get_analysis_type_description
        
        current_task = get_current_task()
        if current_task:
            print(f"当前bio_task: {current_task}")
            if current_task.task_type:
                if isinstance(current_task.task_type, int):
                    description = get_analysis_type_description(current_task.task_type)
                    print(f"当前task_type: {current_task.task_type} - {description}")
                else:
                    print(f"当前task_type: {current_task.task_type}")
            else:
                print("当前task_type: 未设置")
        else:
            print("当前bio_task: 未找到")
            
    except Exception as e:
        print(f"检查状态时出错: {e}")

def simulate_reset_scenarios():
    """模拟各种重置场景"""
    print("\n🧪 模拟重置场景")
    print("-" * 40)
    
    try:
        from bio_task import get_current_task, update_current_task, initialize_bio_task
        
        # 场景1: 设置一个初始值
        print("\n📋 场景1: 设置初始task_type")
        update_current_task(task_type=2)  # Gene Knockout Analysis
        current = get_current_task()
        print(f"设置后: {current.task_type}")
        
        # 场景2: 模拟实验状态更新
        print("\n📋 场景2: 模拟实验状态更新")
        update_current_task(task_type='gene_deletion_analysis_running')
        current = get_current_task()
        print(f"实验运行中: {current.task_type}")
        
        # 场景3: 模拟实验完成
        print("\n📋 场景3: 模拟实验完成")
        update_current_task(task_type='gene_deletion_analysis_completed')
        current = get_current_task()
        print(f"实验完成: {current.task_type}")
        
        # 场景4: 恢复为分析类型
        print("\n📋 场景4: 恢复为分析类型")
        update_current_task(task_type=2)  # 恢复为Gene Knockout Analysis
        current = get_current_task()
        print(f"恢复后: {current.task_type}")
        
        print("\n✅ 模拟完成")
        
    except Exception as e:
        print(f"模拟过程中出错: {e}")

if __name__ == "__main__":
    analyze_task_type_reset_scenarios()
    check_current_task_type_status()
    simulate_reset_scenarios()
