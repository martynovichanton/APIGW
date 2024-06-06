
SITE1_TEST_POOLS = [
    "~Common~testpool99",
    "~Common~testpool99_2"
]

SITE2_TEST_POOLS = [
    "~Common~testpool99",
    "~Common~testpool99_2"
]


#########################################################################################
######## SITE1
#########################################################################################

def f5_site1_update_switch(f5, pools, site1_prio, site2_prio, vip_site2_prio, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if "vip-site2" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{vip_site2_prio}}}\n')
            elif "site1" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{site1_prio}}}\n')
            elif "site2" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{site2_prio}}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"priorityGroup":10}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site1_update_enable(f5, pools, site_to_enable, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if site_to_enable in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"session":"user-enabled", "state":"user-up"}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"session":"user-enabled", "state":"user-up"}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site1_update_forceoffline(f5, pools, site_to_forceoffline, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if site_to_forceoffline in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"session":"user-disabled", "state":"user-down"}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"session":"user-disabled", "state":"user-down"}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site1_update_config(f5, pools, partition_names, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        if any(name in pool.lower() for name in partition_names):
            commands_file.write(f'get---/mgmt/tm/ltm/pool/{pool}/members---\n')

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site1_update_stats(f5, pools, partition_names, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        if any(name in pool.lower() for name in partition_names):
            commands_file.write(f'get---/mgmt/tm/ltm/pool/{pool}/members/stats---\n')

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site1_update_test_switch_site1_to_site2(f5):
    pools = SITE1_TEST_POOLS
    site1_prio = 10
    site2_prio = 80
    vip_site2_prio = 50
    file_name = "API/Actions/F5_SITE1_TEST_SWITCH_SITE1_TO_SITE2/api/f5/commands.txt"
    result = f5_site1_update_switch(f5, pools, site1_prio, site2_prio, vip_site2_prio, file_name)
    return result

def f5_site1_update_test_switch_site2_to_site1(f5):
    pools = SITE1_TEST_POOLS
    site1_prio = 100
    site2_prio = 80
    vip_site2_prio = 50
    file_name = "API/Actions/F5_SITE1_TEST_SWITCH_SITE2_TO_SITE1/api/f5/commands.txt"
    result = f5_site1_update_switch(f5, pools, site1_prio, site2_prio, vip_site2_prio, file_name)
    return result

def f5_site1_update_test_enable_site1(f5):
    pools = SITE1_TEST_POOLS
    site_to_enable = "site1"
    file_name = "API/Actions/F5_SITE1_TEST_ENABLE_SITE1/api/f5/commands.txt"
    result = f5_site1_update_enable(f5, pools, site_to_enable, file_name)
    return result

def f5_site1_update_test_enable_site2(f5):
    pools = SITE1_TEST_POOLS
    site_to_enable = "site2"
    file_name = "API/Actions/F5_SITE1_TEST_ENABLE_SITE2/api/f5/commands.txt"
    result = f5_site1_update_enable(f5, pools, site_to_enable, file_name)
    return result

def f5_site1_update_test_forceoffline_site1(f5):
    pools = SITE1_TEST_POOLS
    site_to_forceoffline = "site1"
    file_name = "API/Actions/F5_SITE1_TEST_FORCEOFFLINE_SITE1/api/f5/commands.txt"
    result = f5_site1_update_forceoffline(f5, pools, site_to_forceoffline, file_name)
    return result

def f5_site1_update_test_forceoffline_site2(f5):
    pools = SITE1_TEST_POOLS
    site_to_forceoffline = "site2"
    file_name = "API/Actions/F5_SITE1_TEST_FORCEOFFLINE_SITE2/api/f5/commands.txt"
    result = f5_site1_update_forceoffline(f5, pools, site_to_forceoffline, file_name)
    return result

def f5_site1_update_config_f501(f5):
    pools = SITE1_TEST_POOLS
    partition_names = ["common", "partition01", "partition03", "partition05"]
    file_name = "API/Actions/F5_SITE1_show_config/api/f501/commands.txt"
    result = f5_site1_update_config(f5, pools, partition_names, file_name)
    return result

def f5_site1_update_config_f502(f5):
    pools = SITE1_TEST_POOLS
    partition_names = ["partition02", "partition04"]
    file_name = "API/Actions/F5_SITE1_show_config/api/f502/commands.txt"
    result = f5_site1_update_config(f5, pools, partition_names, file_name)
    return result

def f5_site1_update_stats_f501(f5):
    pools = SITE1_TEST_POOLS
    partition_names = ["common", "partition01", "partition03", "partition05"]
    file_name = "API/Actions/F5_SITE1_show_stats/api/f501/commands.txt"
    result = f5_site1_update_stats(f5, pools, partition_names, file_name)
    return result

def f5_site1_update_stats_f502(f5):
    pools = SITE1_TEST_POOLS
    partition_names = ["partition02", "partition04"]
    file_name = "API/Actions/F5_SITE1_show_stats/api/f502/commands.txt"
    result = f5_site1_update_stats(f5, pools, partition_names, file_name)
    return result

#########################################################################################
######## SITE2
#########################################################################################

def f5_site2_update_switch(f5, pools, site1_prio, site2_prio, vip_site1_prio, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if "vip-site1" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{vip_site1_prio}}}\n')
            elif "site1" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{site1_prio}}}\n')
            elif "site2" in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"priorityGroup":{site2_prio}}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"priorityGroup":10}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site2_update_enable(f5, pools, site_to_enable, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if site_to_enable in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"session":"user-enabled", "state":"user-up"}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"session":"user-enabled", "state":"user-up"}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site2_update_forceoffline(f5, pools, site_to_forceoffline, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        members = f5.pool_members(pool)
        for member in members["pool_members"]["items"]:
            if site_to_forceoffline in member["name"].lower():
                commands_file.write(f'patch---/mgmt/tm/ltm/pool/{pool}/members/~{member["partition"]}~{member["name"]}---{{"session":"user-disabled", "state":"user-down"}}\n')

            #patch---/mgmt/tm/ltm/pool/~Common~testpool99/members/~Common~testnode1:443---{"session":"user-disabled", "state":"user-down"}

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site2_update_config(f5, pools, partition_names, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        if any(name in pool.lower() for name in partition_names):
            commands_file.write(f'get---/mgmt/tm/ltm/pool/{pool}/members---\n')

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site2_update_stats(f5, pools, partition_names, file_name):
    commands_file = open(file_name, 'w+')

    for pool in pools:
        if any(name in pool.lower() for name in partition_names):
            commands_file.write(f'get---/mgmt/tm/ltm/pool/{pool}/members/stats---\n')

    # read the content for the response
    commands_file.seek(0)
    commands = commands_file.read().splitlines()
    # for command in commands:
    #     print(command)
    commands_file.close()

    # return {"result": "commands updated"}
    return {file_name: commands}

def f5_site2_update_test_switch_site1_to_site2(f5):
    pools = SITE2_TEST_POOLS
    site1_prio = 80
    site2_prio = 100
    vip_site1_prio = 50
    file_name = "API/Actions/F5_SITE2_TEST_SWITCH_SITE1_TO_SITE2/api/f5/commands.txt"
    result = f5_site2_update_switch(f5, pools, site1_prio, site2_prio, vip_site1_prio, file_name)
    return result

def f5_site2_update_test_switch_site2_to_site1(f5):
    pools = SITE2_TEST_POOLS
    site1_prio = 80
    site2_prio = 10
    vip_site1_prio = 50
    file_name = "API/Actions/F5_SITE2_TEST_SWITCH_SITE2_TO_SITE1/api/f5/commands.txt"
    result = f5_site2_update_switch(f5, pools, site1_prio, site2_prio, vip_site1_prio, file_name)
    return result

def f5_site2_update_test_enable_site1(f5):
    pools = SITE2_TEST_POOLS
    site_to_enable = "site1"
    file_name = "API/Actions/F5_SITE2_TEST_ENABLE_SITE1/api/f5/commands.txt"
    result = f5_site2_update_enable(f5, pools, site_to_enable, file_name)
    return result

def f5_site2_update_test_enable_site2(f5):
    pools = SITE2_TEST_POOLS
    site_to_enable = "site2"
    file_name = "API/Actions/F5_SITE2_TEST_ENABLE_SITE2/api/f5/commands.txt"
    result = f5_site2_update_enable(f5, pools, site_to_enable, file_name)
    return result

def f5_site2_update_test_forceoffline_site1(f5):
    pools = SITE2_TEST_POOLS
    site_to_forceoffline = "site1"
    file_name = "API/Actions/F5_SITE2_TEST_FORCEOFFLINE_SITE1/api/f5/commands.txt"
    result = f5_site2_update_forceoffline(f5, pools, site_to_forceoffline, file_name)
    return result

def f5_site2_update_test_forceoffline_site2(f5):
    pools = SITE2_TEST_POOLS
    site_to_forceoffline = "site2"
    file_name = "API/Actions/F5_SITE2_TEST_FORCEOFFLINE_SITE2/api/f5/commands.txt"
    result = f5_site2_update_forceoffline(f5, pools, site_to_forceoffline, file_name)
    return result

def f5_site2_update_config_f501(f5):
    pools = SITE2_TEST_POOLS
    partition_names = ["common", "partition01", "partition03", "partition05"]
    file_name = "API/Actions/F5_SITE2_show_config/api/f501/commands.txt"
    result = f5_site2_update_config(f5, pools, partition_names, file_name)
    return result

def f5_site2_update_config_f502(f5):
    pools = SITE2_TEST_POOLS
    partition_names = ["partition02", "partition04"]
    file_name = "API/Actions/F5_SITE2_show_config/api/f502/commands.txt"
    result = f5_site2_update_config(f5, pools, partition_names, file_name)
    return result

def f5_site2_update_stats_f501(f5):
    pools = SITE2_TEST_POOLS
    partition_names = ["common", "partition01", "partition03", "partition05"]
    file_name = "API/Actions/F5_SITE2_show_stats/api/f501/commands.txt"
    result = f5_site2_update_stats(f5, pools, partition_names, file_name)
    return result

def f5_site2_update_stats_f502(f5):
    pools = SITE2_TEST_POOLS
    partition_names = ["partition02", "partition04"]
    file_name = "API/Actions/F5_SITE2_show_stats/api/f502/commands.txt"
    result = f5_site2_update_stats(f5, pools, partition_names, file_name)
    return result

#########################################################################################
######## Update generic
#########################################################################################

def f5_site1_update_commands(f5):
    results = {}
    results.update(f5_site1_update_test_switch_site1_to_site2(f5))
    results.update(f5_site1_update_test_switch_site2_to_site1(f5))
    results.update(f5_site1_update_test_enable_site1(f5))
    results.update(f5_site1_update_test_enable_site2(f5))
    results.update(f5_site1_update_test_forceoffline_site1(f5))
    results.update(f5_site1_update_test_forceoffline_site2(f5))
    results.update(f5_site1_update_config_f501(f5))
    results.update(f5_site1_update_config_f502(f5))
    results.update(f5_site1_update_stats_f501(f5))
    results.update(f5_site1_update_stats_f502(f5))
    return results

def f5_site2_update_commands(f5):
    results = {}
    results.update(f5_site2_update_test_switch_site1_to_site2(f5))
    results.update(f5_site2_update_test_switch_site2_to_site1(f5))
    results.update(f5_site2_update_test_enable_site1(f5))
    results.update(f5_site2_update_test_enable_site2(f5))
    results.update(f5_site2_update_test_forceoffline_site1(f5))
    results.update(f5_site2_update_test_forceoffline_site2(f5))
    results.update(f5_site2_update_config_f501(f5))
    results.update(f5_site2_update_config_f502(f5))
    results.update(f5_site2_update_stats_f501(f5))
    results.update(f5_site2_update_stats_f502(f5))
    return results