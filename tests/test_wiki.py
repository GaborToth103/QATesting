import pandas as pd
import re
from typing import List, Tuple, Dict



# Example usage
if __name__ == "__main__":
    # Sample DataFrame (Pandas table)

    data = [['1,7', '5,1', '11,2', '17,1', '22,3', '25,3', '27,4', '27,0', '23,4', '17,6', '9,5', '3,8', '16,0'], ['−1,8', '0,9', '5,6', '11,1', '16,2', '19,2', '20,8', '20,2', '16,5', '11,0', '5,1', '0,6', '10,5'], ['−4,8', '−2,5', '0,9', '5,5', '10,3', '13,4', '14,4', '13,9', '10,4', '5,6', '1,7', '−2,1', '5,6'], ['29', '25', '29', '41', '51', '72', '50', '57', '34', '26', '41', '40', '495'], ['62', '87', '142', '180', '234', '255', '288', '266', '210', '170', '80', '51', '2025'], ['Forrás: Országos Meteorológiai Szolgálat']]  

    df = pd.DataFrame(data)
    
    print(df)