import pandas as pd
from itertools import combinations
import re
# This file is used for all the normalizations

def is_list_or_set(item):
    return isinstance(item, (list, set))

def is_superkey(relation, determinant):
    grouped = relation.groupby(
        list(determinant)).size().reset_index(name='count')
    return not any(grouped['count'] > 1)

def powerset(s):
    x = len(s)
    for i in range(1 << x):
        yield [s[j] for j in range(x) if (i & (1 << j)) > 0]

def closure(attributes, fds):
    closure_set = set(attributes)
    while True:
        closure_before = closure_set.copy()
        for det, deps in fds.items():
            if set(det).issubset(closure_set):
                closure_set.update(deps)
        if closure_before == closure_set:
            break
    return closure_set

def bcnf_decomposition(relation, dependencies):
    decomposed_tables = []
    for det, dep in dependencies.items():
        closure_set = closure(set(det), dependencies)
        if not closure_set.issuperset(relation.columns):
            cols = list(det) + dep
            if set(cols).issubset(relation.columns) and not set(cols) == set(relation.columns):
                new_table = relation[list(det) + dep].drop_duplicates()
                decomposed_tables.append(new_table)
                relation = relation.drop(columns=dep)
    if not decomposed_tables:
        return [relation]
    else:
        return [relation] + decomposed_tables

def is_1nf(relation):
    if relation.empty:
        return False
    for column in relation.columns:
        unique_types = relation[column].apply(type).nunique()
        if unique_types > 1:
            return False
        if relation[column].apply(lambda x: isinstance(x, (list, dict, set))).any():
            return False
    return True

def is_2nf(primary_key, dependencies, relation):
    non_prime_attributes = [
        col for col in relation.columns if col not in primary_key]
    for determinant, dependents in dependencies.items():
        if set(determinant).issubset(primary_key) and set(determinant) != set(primary_key):
            if any(attr in non_prime_attributes for attr in dependents):
                return False
    return True

def is_3nf(relations, dependencies):
    primary_keys = [key for key in dependencies]
    non_key_attributes = [item for sublist in dependencies.values()
                          for item in sublist]
    for relation_name, relation in relations.items():
        for det, dep in dependencies.items():
            if set(det).issubset(set(relation.columns)) and not set(det).issubset(primary_keys) and set(dep).issubset(non_key_attributes):
                return False
    return True

def is_bcnf(relations, primary_key, dependencies):
    for relation_name, relation in relations.items():
        all_attributes = set(relation.columns)
        for det, deps in dependencies.items():
            for dep in deps:
                if dep not in det:
                    if all_attributes - closure(det, dependencies):
                        return False
    return True

def is_4nf(relations, mvd_dependencies):
    for relation_name, relation in relations.items():
        for determinant, dependents in mvd_dependencies.items():
            for dependent in dependents:
                if isinstance(determinant, tuple):
                    determinant_cols = list(determinant)
                else:
                    determinant_cols = [determinant]
                if all(col in relation.columns for col in determinant_cols + [dependent]):
                    grouped = relation.groupby(determinant_cols)[
                        dependent].apply(set).reset_index()
                    if len(grouped) < len(relation):
                        print(
                            f"Multi-valued dependency violation: {determinant} ->-> {dependent}")
                        return False
    return True

def is_5nf(relations):
    candidate_keys_dict = {}
    for relation_name, relation in relations.items():
        print(relation)
        user_input = input(
            "Give the candidate keys for above relation: ")
        print('\n')
        tuples = re.findall(r'\((.*?)\)', user_input)
        candidate_keys = [tuple(map(str.strip, t.split(','))) for t in tuples]
        candidate_keys_dict[relation_name] = candidate_keys
    print(f'Candidate Keys for tables are:')
    print(candidate_keys_dict)
    print('\n')
    for relation_name, relation in relations.items():
        candidate_keys = candidate_keys_dict[relation_name]
        data_tuples = [tuple(row) for row in relation.to_numpy()]
        def project(data, attributes):
            return {tuple(row[attr] for attr in attributes) for row in data}
        def is_superkey(attributes):
            for key in candidate_keys:
                if set(key).issubset(attributes):
                    return True
            return False, candidate_keys_dict
        for i in range(1, len(relation.columns)):
            for attrs in combinations(relation.columns, i):
                if is_superkey(attrs):
                    continue
                projected_data = project(data_tuples, attrs)
                complement_attrs = set(relation.columns) - set(attrs)
                complement_data = project(data_tuples, complement_attrs)
                joined_data = {(row1 + row2)
                               for row1 in projected_data for row2 in complement_data}
                if set(data_tuples) != joined_data:
                    print("Failed to give 5NF, please check for attributes:", attrs)
                    return False, candidate_keys_dict
    return True, candidate_keys_dict

def first_nf(relation, primary_key):
    relations = {}
    one_flag = is_1nf(relation)
    if one_flag:
        relations[primary_key] = relation
        return relations, one_flag
    else:
        for col in relation.columns:
            if relation[col].apply(is_list_or_set).any():
                relation = relation.explode(col)
        print('RELATION AFTER 1NF')
        print(relation)
        print('\n')
        relations[primary_key] = relation
        return relations, one_flag

def second_nf(relation, primary_key, dependencies):
    relation = relation[primary_key]
    relations = {}
    rm_cols = []
    two_flag = is_2nf(primary_key, dependencies, relation)
    if two_flag:
        relations[primary_key] = relation
        return relations, two_flag
    else:
        print('RELATIONS AFTER 2NF')
        print('\n')
        non_prime_attributes = [
            col for col in relation.columns if col not in primary_key]
        for det, dep in dependencies.items():
            if set(det).issubset(primary_key) and set(det) != set(primary_key):
                if any(attr in dep for attr in non_prime_attributes):
                    new_relation = relation[list(det) + dep].drop_duplicates()
                    relations[tuple(det)] = new_relation
                    for attr in dep:
                        if attr not in det and attr not in rm_cols:
                            rm_cols.append(attr)
        relation.drop(columns=rm_cols, inplace=True)
        relations[primary_key] = relation
        for relation in relations:
            print(relations[relation])
            print('\n')
        return relations, two_flag

def third_nf(relations, primary_key, dependencies):
    three_relations = {}
    three_flag = is_3nf(relations, dependencies)
    if three_flag:
        return relations, three_flag
    else:
        print('RELATIONS AFTER 3NF')
        print('\n')
        for relation_name, relation in relations.items():
            for det, dep in dependencies.items():
                if set(det).issubset(set(relation.columns)) and not set(dep).issubset(det):
                    new_cols = list(set(det).union(dep))
                    if set(new_cols).issubset(set(relation.columns)) and not set(new_cols) == set(relation.columns):
                        table1_cols = list(det) + dep
                        table2_cols = list(set(relation.columns) - set(dep))
                        new_table1 = relation[table1_cols].drop_duplicates(
                        ).reset_index(drop=True)
                        new_table2 = relation[table2_cols].drop_duplicates(
                        ).reset_index(drop=True)
                        three_relations[tuple(det)] = new_table1
                        three_relations[relation_name] = new_table2
                        break
            else:
                three_relations[relation_name] = relation
        for relation in three_relations:
            print(three_relations[relation])
            print('\n')
        return three_relations, three_flag

def bc_nf(relations, primary_key, dependencies):
    bcnf_relations = {}
    bcnf_final = {}
    bcnf_flag = is_bcnf(relations, primary_key, dependencies)
    if bcnf_flag:
        return relations, bcnf_flag
    else:
        print('RELATIONS AFTER BCNF')
        print('\n')
        for relation_name, relation in relations.items():
            for det, dep in dependencies.items():
                closure_set = closure(set(det), dependencies)
                if not closure_set.issuperset(relation.columns):
                    cols = list(det) + dep
                    if set(cols).issubset(relation.columns) and not set(cols) == set(relation.columns):
                        new_table = relation[list(det) + dep].drop_duplicates()
                        bcnf_relations[tuple(det)] = new_table
                        relation = relation.drop(columns=dep)
            bcnf_relations[relation_name] = relation
        for rel in bcnf_relations:
            print(bcnf_relations[rel])
            print('\n')
    return bcnf_relations, bcnf_flag

def fourth_nf(relations, mvd_dependencies):
    four_relations = {}
    four_flag = is_4nf(relations, mvd_dependencies)
    if four_flag:
        return relations, four_flag
    else:
        print('RELATIONS AFTER 4NF')
        for relation_name, relation in relations.items():
            for determinant, dependents in mvd_dependencies.items():
                for dependent in dependents:
                    if isinstance(determinant, tuple):
                        determinant_cols = list(determinant)
                    else:
                        determinant_cols = [determinant]
                    if all(col in relation.columns for col in determinant_cols + [dependent]):
                        grouped = relation.groupby(determinant_cols)[
                            dependent].apply(set).reset_index()
                        if len(grouped) < len(relation):
                            table_1 = relation[determinant_cols +
                                               [dependent]].drop_duplicates()
                            four_relations[tuple(determinant_cols)] = table_1
                            table_2 = relation[determinant_cols + [col for col in relation.columns if col not in [
                                dependent] + determinant_cols]].drop_duplicates()
                            four_relations[relation_name] = table_2
                            break
                else:
                    continue
                break
            else:
                four_relations[relation_name] = relation
    if len(four_relations) == len(relations):
        return four_relations
    else:
        return fourth_nf(four_relations, mvd_dependencies)

def decompose_5nf(relation_name, dataframe, candidate_keys):
    def project(df, attributes):
        return df[list(attributes)].drop_duplicates().reset_index(drop=True)
    def is_lossless(df, df1, df2):
        common_columns = set(df1.columns) & set(df2.columns)
        if not common_columns:
            return False
        joined_df = pd.merge(df1, df2, how='inner', on=list(common_columns))
        return df.equals(joined_df)
    decomposed_tables = [dataframe]
    for key in candidate_keys:
        new_tables = []
        for table in decomposed_tables:
            if set(key).issubset(set(table.columns)):
                table1 = project(table, key)
                remaining_columns = set(table.columns) - set(key)
                table2 = project(table, remaining_columns | set(key))
                if is_lossless(table, table1, table2):
                    new_tables.extend([table1, table2])
                else:
                    new_tables.append(table)
            else:
                new_tables.append(table)
        decomposed_tables = new_tables
    return decomposed_tables

def fifth_nf(relations, primary_key, dependencies):
    five_relations = {}
    five_flag, candidate_keys_dict = is_5nf(relations)
    if five_flag:
        return relations, five_flag
    else:
        print('RELATIONS AFTER 5NF')
        for relation_name, relation in relations:
            candidate_keys = candidate_keys_dict[relation_name]
            decomposed_relations = decompose_5nf(
                relation_name, relation, candidate_keys)
            five_relations.append(decomposed_relations)
    return five_relations, five_flag