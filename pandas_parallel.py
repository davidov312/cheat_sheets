##############
# Author: David Dov
# Date 11.5.22
#
# multiprocessing and pandas examples
# 1. Apply a function to df group by using a single thread
# 2. Apply a function to df group by with async parallel multiprocessing
# 3. Apply a function to df in parallel by splitting df into n dataframes (n=number of threads)
# Code is partly based on : https://towardsdatascience.com/make-your-own-super-pandas-using-multiproc-1c04f41944a1

#  imports
import pandas as pd, numpy as np
from multiprocessing import get_context, cpu_count, Pool
from typing import Callable

# util functions
def my_square(df: pd.DataFrame) -> pd.DataFrame: 
    df_out = df.copy()
    df_out['square'] = df_out.my_val.pow(2)
    return df_out


def apply_my_func_group_by_single_core(df_groupby, func: Callable) -> pd.DataFrame: 
    result_list = []
    for _, group_df in df_groupby:
        print(type(group_df))
        result_list.append(func(group_df))
    result_df = pd.concat(result_list, axis=0, ignore_index=True, sort=False)  
    return result_df


def apply_my_func_group_by_async(df_groupby, func: Callable) -> pd.DataFrame: 
    pool = get_context().Pool(processes=cpu_count())
    result_async = [pool.apply_async(func, args=(group_df,))
                for _, group_df in df_groupby]
    
    pool.close()
    pool.join() # wait untill parallel loop ends end
    result_list = [res.get() for res in result_async]

    result_df = pd.concat(result_list, axis=0, ignore_index=True, sort=False)  
    return(result_df)

def apply_my_func_sync(df: pd.DataFrame, func: Callable) -> pd.DataFrame:
    df_split = np.array_split(df, cpu_count())
    pool = Pool(cpu_count())
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


# main function
def main():
    df = pd.DataFrame(data={'my_val': range(20),
                            'my_group': list(range(4))*5})
                        
    result_df1 = apply_my_func_group_by_single_core(df.groupby('my_group'), my_square)
    result_df2 = apply_my_func_group_by_async(df.groupby('my_group'), my_square)
    result_df3 = apply_my_func_sync(df, my_square)

    result_df1 = result_df1.sort_values(by='my_val').reset_index(drop=True) 
    result_df2 = result_df2.sort_values(by='my_val').reset_index(drop=True) 
    result_df3 = result_df3.sort_values(by='my_val').reset_index(drop=True) 

    assert result_df1.equals(result_df2)
    assert result_df1.equals(result_df3)
    print('All 3 calculations give the same result')


if __name__ == "__main__":
    main()