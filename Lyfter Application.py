#!/usr/bin/env python
# coding: utf-8

# # Lyfter Application
# 
# Lyfter is a Python application that records the workouts of the user, utilizing knowledge of primary, secondary, and tertiary movers for each exercise logged to calculate total sets per muscle group worked per week. Lyfter also employs the use of an SQLite database to store workout information, total weekly muscle sets, and workout volume for later visualization in order to track the user’s progression over time.

# In[10]:


import sqlite3
from datetime import datetime, date, timedelta

# This is the muscle set dictionary that will be utilized every time workout data is input, whether it be a single
# session, or multiple workouts input at once. Python will receive the workout data, convert it into a nested dict,
# and update the muscle sets dict using the nested dict. After this, the data will be stored in SQL.

muscle_sets = {'Lats':0, 'Lower_Back':0,'Trapezius':0,
               'Front_Deltoids':0, 'Side_Deltoids':0, 'Rear_Deltoids':0,
               'Pectorals':0,
               'Triceps':0, 'Biceps':0, 'Forearms':0,
               'Abdominals':0,
               'Glutes':0, 'Hamstrings':0, 'Quadriceps':0, 'Calves':0,
               'Neck':0}

# This is the exercise list dictionary that functions reference in order to determine what muscles were being worked
# by which exercise. Based on whether the muscle is a primary, secondary, or tertiary mover, the number of sets
# completed per muscle will be adjusted accordingly by a "mover constant."

exercise_list = {
     'Barbell Bench Press': {'Pectorals': 1, 'Triceps': 1, 'Front_Deltoids': 1},
     'Close Grip Barbell Bench Press': {'Pectorals': 1, 'Triceps': 1, 'Front_Deltoids': 1},
     'DB Bench Press': {'Pectorals': 1, 'Triceps': 1, 'Front_Deltoids': 1},
     'DB Incline Bench Press': {'Pectorals':1,'Front_Deltoids':1, 'Triceps':1},
     'Decline Press Machine': {'Pectorals':1, 'Triceps':2},
     'Back Squat': {'Quadriceps': 1, 'Glutes': 2, 'Lower_Back': 3},
     'Paused Back Squats': {'Quadriceps': 1, 'Glutes': 2, 'Lower_Back': 3},
     'Front Squat': {'Quadriceps': 1, 'Trapezius': 3},
     'Paused Front Squats': {'Quadriceps': 1, 'Trapezius': 3},
     'Smith Machine Hip Thrust': {'Glutes': 1, 'Hamstrings': 2},
     'Barbell Overhead Press': {'Front_Deltoids': 1,'Side_Deltoids': 2,'Triceps': 2},
     'DB Overhead Press': {'Front_Deltoids': 1,'Side_Deltoids': 2,'Triceps': 2},
     'DB Lateral Raises': {'Side_Deltoids':1},
     'Lateral Raise Machine': {'Side_Deltoids':1},
     'Deadlift': {'Hamstrings': 1,'Glutes': 1,'Lower_Back': 1,'Forearms': 1,'Quadriceps': 2,'Trapezius': 2},
     'Hex Bar Deadlift': {'Hamstrings': 1,'Glutes': 1,'Lower_Back': 1,'Quadriceps': 2,'Trapezius': 2},
     'Romanian Deadlift': {'Hamstrings': 1,'Glutes': 1,'Lower_Back': 1,'Forearms': 2},
     'Unilateral Leg Press': {'Quadriceps': 1},
     'Seated Calf Raises': {'Calves': 1},
     'Seated Calf Press Machine': {'Calves':1},
     'Abdominal Crunch Machine': {'Abdominals': 1},
     'Decline Crunch': {'Abdominals': 1},
     'Seated Leg Curls': {'Hamstrings': 1},
     'Lying Leg Curls': {'Hamstrings': 1},
     'Gliding Leg Curls': {'Hamstrings': 1, 'Glutes': 3},
     'Leg Extensions': {'Quadriceps': 1},
     'Back Extensions': {'Lower_Back': 1, 'Hamstrings':3, 'Glutes': 3},
     'Single DB Split Squat': {'Quadriceps': 1, 'Hamstrings': 2,'Glutes': 2},
     'DB Split Squat': {'Quadriceps': 1, 'Hamstrings': 2, 'Glutes': 2},
     'Leg Press Calf Raises': {'Calves': 1},
     'Cable Bicep Curls': {'Biceps': 1},
     'Cable Flys': {'Pectorals': 1},
     'Rear Delt Facepulls': {'Rear_Deltoids':1},
     'Barbell Pendlay Row': {'Trapezius':1, 'Lats':1, 'Biceps':2, 'Rear_Deltoids':2, 'Lower_Back':3},
     'Barbell Bent Over Row': {'Trapezius':1, 'Lats':1, 'Biceps':2, 'Rear_Deltoids':2, 'Lower_Back':3},
     'Lat Pulldowns': {'Lats':1, 'Trapezius':2, 'Biceps':2},
     'EZ Bar Wrist Curls': {'Forearms':1},
     'Walking DB Lunges': {'Quadriceps':1, 'Hamstrings':1,'Glutes':1},
     'Ab Wheel Rollouts': {'Abdominals':1},
     'DB Bicep Curls': {'Biceps':1},
     'EZ Bar Bicep Curls': {'Biceps':1},
     'Machine Preacher Curls': {'Biceps':1},
     'Reverse Pec Deck': {'Rear_Deltoids':1},
     'Pull Ups': {'Lats':1, 'Trapezius':1, 'Biceps':2},
     'Low Row Machine': {'Trapezius':1, 'Lats':2, 'Rear_Deltoids':2},
     'High Row Machine': {'Trapezius':1, 'Lats':2, 'Rear_Deltoids':2},
     'French Press': {'Triceps':1}
}


# In[11]:


# Creates the workout data dictionary with user input.

def create_workout_data():
    number_of_workouts = int(input("How many workouts are being recorded? "))
    workout_dictionary = {}
    for i in range(number_of_workouts):
        if number_of_workouts == 1:
            date = input("What is the date of the workout? Please input the date in YYYY-MM-DD format. ")
        else:
            date = input('''What is the date of workout number ''' + str(i+1) + '''? 
            Please input the date in YYYY-MM-DD format. ''')
        number_of_exercises = int(input("How many exercises are in the workout? "))
        exercises = {}
        for i in range(number_of_exercises):
            rw_dict = {}
            exercise = input("What is exercise number " + str(i+1) + "? ")
            num_sets = int(input("How many working sets for this exercise? "))
            equal_rw = input("Are reps and weight the same throughout all working sets? (Yes / No) ").strip().lower()
            while equal_rw not in ('yes','no'):
                equal_rw = input('''Are reps and weight the same throughout all 
                                    working sets? (Yes / No) ''').strip().lower()
            if equal_rw in ('yes'):
                reps = int(input("How many reps for each set? "))
                weight = float(input("How much weight for each set? "))
                for i in range(num_sets):
                    rw_dict.update({i+1:{'reps':reps,'weight':weight}})
            elif equal_rw in ('no'):
                for i in range(num_sets):
                    reps = int(input("How many reps for set " + str(i+1) + "? "))
                    weight = float(input("How much weight for set " + str(i+1) + "? "))
                    rw_dict.update({i+1:{'reps':reps,'weight':weight}})
            exercises.update({exercise:rw_dict})
        workout_dictionary.update({date:exercises})
    return workout_dictionary

# TEST create_workout_data()


# Function that takes muscle sets dictionary and a week id and updates the WeeklyMuscleSets table in SQL.

def update_weekly_muscle_sets_table_in_sql(muscle_sets,week_id):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()
    
    for muscle in muscle_sets.keys():# Updates SQL table with the muscle_set data for that week
                    num_sets =  muscle_sets.get(muscle)
                    if num_sets != 0:
                        sql_statement = f'''UPDATE WeeklyMuscleSets 
                                            SET {muscle} = {muscle} + (:num_sets) 
                                            WHERE WeekID=(:week_id);'''
                        parameters = {'num_sets':num_sets,'week_id':week_id}
                        c.execute(sql_statement,parameters)
                        
    conn.commit()
    conn.close()
    
    
# Function that takes the workout dictionary created by "create_workout_data" and preps the data to be inserted into
# the WeeklyMuscleSets table in SQL.

def update_muscle_sets_in_sql_from_py(workout_dictionary):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()
    
    unique_weeks = []
    
    for date in workout_dictionary.keys():
        week_number = int(datetime.strptime(date,'%Y-%m-%d').strftime('%V'))
        if week_number not in unique_weeks:
            unique_weeks.append(week_number)
    
    for date in workout_dictionary.keys():
        week_number = int(datetime.strptime(date,'%Y-%m-%d').strftime('%V'))
        for week_id in unique_weeks:
            muscle_sets = {'Lats':0, 'Lower_Back':0,'Trapezius':0,
               'Front_Deltoids':0, 'Side_Deltoids':0, 'Rear_Deltoids':0,
               'Pectorals':0,
               'Triceps':0, 'Biceps':0, 'Forearms':0,
               'Abdominals':0,
               'Glutes':0, 'Hamstrings':0, 'Quadriceps':0, 'Calves':0,
               'Neck':0}
            if week_id == week_number:
                daily_exercise_volume = workout_dictionary.get(date)
                for exercise,set_volume in daily_exercise_volume.items():
                    muscle_groups = exercise_list.get(exercise)
                    for muscle,mover_var in muscle_groups.items():
                        if mover_var == 1:
                            muscle_sets.update({muscle:(len(set_volume) + muscle_sets.get(muscle))})
                        elif mover_var == 2:
                            muscle_sets.update({muscle:(len(set_volume)*(2/3) + muscle_sets.get(muscle))})
                        else:
                            muscle_sets.update({muscle:(len(set_volume)*(1/3) + muscle_sets.get(muscle))})
                            
            update_weekly_muscle_sets_table_in_sql(muscle_sets,week_id)
            
            
# Function that takes the workout dictionary created by "create_workout_data" and updates WorkoutTable in SQL.

def update_workout_table_in_sql_from_py(workout_dictionary):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()
    
    for date in workout_dictionary.keys():
        workout_data = []
        workout = workout_dictionary.get(date)
        for exercise in workout.keys():
            working_sets = workout.get(exercise)
            for work_set in working_sets.keys():
                reps_weight = working_sets.get(work_set)
                workout_data.append((date,exercise,work_set,reps_weight.get('reps'),reps_weight.get('weight')))

        for element in workout_data:
            sql_date = element[0]
            sql_exercise = element[1]
            sql_set_number = element[2]
            sql_reps = element[3]
            sql_weight = element[4]

            sql_statement = '''INSERT INTO WorkoutTable 
                                VALUES (:sql_date,
                                        :sql_exercise,
                                        :sql_set_number,
                                        :sql_reps,
                                        :sql_weight);'''

            parameters = {'sql_date':sql_date,
                          'sql_exercise':sql_exercise,
                          'sql_set_number':sql_set_number,
                          'sql_reps':sql_reps,
                          'sql_weight':sql_weight}

            c.execute(sql_statement,parameters)

    conn.commit()
    conn.close()
    
    
# User inputs their workout(s) and updates both workout data AND weekly muscle sets in SQL.

def insert_new_workout_into_sql():
    workout_dictionary = create_workout_data()
    
    update_muscle_sets_in_sql_from_py(workout_dictionary)
    
    update_workout_table_in_sql_from_py(workout_dictionary)


# In[12]:


# Updates WeeklyMuscleSets from a muscle set dictionary accquired from WorkoutTable.

def update_all_weekly_muscle_sets_in_sql_from_workout_table(muscle_sets):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()

    for muscle in muscle_sets.keys():
        num_sets =  muscle_sets.get(muscle)
        if num_sets != 0:
            sql_statement = f"UPDATE WeeklyMuscleSets SET {muscle} = (:num_sets) WHERE WeekID=(:week_id);"
            parameters = {'num_sets':num_sets,'week_id':week_id}
            c.execute(sql_statement,parameters)
            
    conn.commit()
    conn.close()
    
# Updates ALL of the rows in WeeklyMuscleSets from data accquired from WorkoutTable.

def update_all_weekly_muscle_sets_in_sql():
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()

    c.execute('SELECT Date,Exercise,COUNT(Exercise) FROM WorkoutTable GROUP BY Date,Exercise;')
    exercise_data_sql = c.fetchall()


    date_exercise_number_of_sets = [[int(datetime.strptime(data[0],'%Y-%m-%d').strftime('%V')),
                                 data[1],
                                 data[2]] for data in exercise_data_sql]


    unique_week_id = []
    for data in date_exercise_number_of_sets:
        week_id = data[0]
        if week_id not in unique_week_id:
            unique_week_id.append(week_id)

    for week_id in unique_week_id:

        muscle_sets = {'Lats':0, 'Lower_Back':0,'Trapezius':0,
                       'Front_Deltoids':0, 'Side_Deltoids':0, 'Rear_Deltoids':0,
                       'Pectorals':0,
                       'Triceps':0, 'Biceps':0, 'Forearms':0,
                       'Abdominals':0,
                       'Glutes':0, 'Hamstrings':0, 'Quadriceps':0, 'Calves':0,
                       'Neck':0}

        for data in date_exercise_number_of_sets:
            week_num = data[0]
            exercise = data[1]
            number_of_sets = data[2]

            if week_num == week_id:
                muscle_groups = exercise_list.get(exercise)
                for muscle,mover_var in muscle_groups.items():
                    if mover_var == 1:
                        muscle_sets[muscle] += number_of_sets
                    elif mover_var == 2:
                        muscle_sets[muscle] += number_of_sets*(2/3)
                    else:
                        muscle_sets[muscle] += number_of_sets*(1/3)
                        

        update_all_muscle_sets_in_sql_from_workout_table(muscle_sets)
                        
    conn.commit()
    conn.close()


# In[13]:


# Function gets the start and end date from a week number for the purpose of SQL querying.

def give_week_start_and_end_date_from_week_number(week_number):
    d = '{}-W{}'.format('2019',week_number)
    start_date = datetime.strptime(d + '-1', '%G-W%V-%u').date()
    end_date = datetime.strptime(d + '-7', '%G-W%V-%u').date()
    return [str(start_date),str(end_date)]


# Function that returns "date_exercise_number_of_sets", a list that returns information from WorkoutTable in SQL in
# a format that can be utilized by later functions.

def get_weekly_muscle_sets_from_sql_workout_table(week_id):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()

    start_date = give_week_start_and_end_date_from_week_number(week_id)[0]
    end_date = give_week_start_and_end_date_from_week_number(week_id)[-1]

    sql_statement = '''SELECT Date,Exercise,COUNT(Exercise) 
                    FROM WorkoutTable
                    WHERE Date BETWEEN (:start_date) AND (:end_date)
                    GROUP BY Date,Exercise'''
    parameters = {'start_date':start_date,'end_date':end_date}

    c.execute(sql_statement,parameters)
    exercise_data_sql = c.fetchall()
    
    date_exercise_number_of_sets = [[int(datetime.strptime(data[0],'%Y-%m-%d').strftime('%V')),
                                 data[1],
                                 data[2]] for data in exercise_data_sql]
    
    conn.commit()
    conn.close()
    
    return date_exercise_number_of_sets


# Utilizes the "date_exercise_number_of_sets" list to create a python muscle set dictionary.

def create_py_muscle_sets_from_sql_workout_table(date_exercise_number_of_sets):
        
        muscle_sets = {'Lats':0.0, 'Lower_Back':0.0,'Trapezius':0.0,
                   'Front_Deltoids':0.0, 'Side_Deltoids':0.0, 'Rear_Deltoids':0.0,
                   'Pectorals':0.0,
                   'Triceps':0.0, 'Biceps':0.0, 'Forearms':0.0,
                   'Abdominals':0.0,
                   'Glutes':0.0, 'Hamstrings':0.0, 'Quadriceps':0.0, 'Calves':0.0,
                   'Neck':0.0}
        
        for data in date_exercise_number_of_sets:
            week_number = data[0]
            exercise = data[1]
            number_of_sets = data[2]
            
            muscle_groups = exercise_list.get(exercise)
            for muscle,mover_var in muscle_groups.items():
                if mover_var == 1:
                    muscle_sets[muscle] += number_of_sets
                elif mover_var == 2:
                    muscle_sets[muscle] += number_of_sets*(2/3)
                else:
                    muscle_sets[muscle] += number_of_sets*(1/3)
                    
        return muscle_sets

    
# Updates the WeeklyMuscleSets table with information gained from the previous functions.

def update_weekly_muscle_sets_in_sql_from_workout_table(muscle_sets,week_id):
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()
    
    for muscle in muscle_sets.keys():# Updates SQL table with the muscle_set data for that week
        num_sets =  muscle_sets.get(muscle)
        if num_sets != 0:
            sql_statement = f'''UPDATE WeeklyMuscleSets 
                                SET {muscle} = (:num_sets)
                                WHERE WeekID=(:week_id);'''
            parameters = {'num_sets':num_sets,'week_id':week_id}
            c.execute(sql_statement,parameters)
            
    conn.commit()
    conn.close()
    
    
# Takes a week number and updates the WeeklyMuscleSets table after a change in the data.

def specific_weekly_muscle_sets_update_sql(week_number):
#     week_number = int(datetime.strptime(date,'%Y-%m-%d').strftime('%V'))
    
    week_number_exercise_number_of_sets = get_weekly_muscle_sets_from_sql_workout_table(week_number)
    
    weekly_muscle_sets = create_py_muscle_sets_from_sql_workout_table(week_number_exercise_number_of_sets)
    
    update_weekly_muscle_sets_in_sql_from_workout_table(weekly_muscle_sets,week_number)


# In[14]:


# Function that updates reps and weight in SQL; returns week number for use with the function responsible for
# updating the WeeklyMuscleSets table.

def update_reps_and_weight():
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()

    date = input("What is the date of the workout you want to update? YYYY-MM-DD ")
    week_number = int(datetime.strptime(date,'%Y-%m-%d').strftime('%V'))
    exercise = input("What exercise do you want to update? ")
    set_number = int(input("What set number do you want to update? "))
    
    rw = input("Do you want to update reps, weight, or both? ").strip().lower()
    while rw not in ('reps','weight','both'):
        rw = input("Do you want to update reps, weight, or both? ").strip().lower()
    
    if rw == 'reps':
        new_reps = int(input("How many reps? "))
        sql_statement = '''UPDATE WorkoutTable 
                            SET Reps=(:new_reps) 
                            WHERE Date=(:date) AND Exercise=(:exercise) AND SetNumber=(:set_number);'''
        parameters = {'new_reps':new_reps,'date':date,'exercise':exercise,'set_number':set_number}
        c.execute(sql_statement,parameters)
    elif rw == 'weight':
        new_weight = float(input("How much weight? "))
        sql_statement = '''UPDATE WorkoutTable 
                            SET Weight=(:new_weight) 
                            WHERE Date=(:date) AND Exercise=(:exercise) AND SetNumber=(:set_number);'''
        parameters = {'new_weight':new_weight,'date':date,'exercise':exercise,'set_number':set_number}
        c.execute(sql_statement,parameters)
    else:
        new_reps = int(input("How many reps? "))
        new_weight = float(input("How much weight? "))
        sql_statement = '''UPDATE WorkoutTable 
                            SET Reps=(:new_reps), Weight=(:new_weight) 
                            WHERE Date=(:date) AND Exercise=(:exercise) AND SetNumber=(:set_number);'''
        parameters = {'new_reps':new_reps,'new_weight':new_weight,'date':date,'exercise':exercise,'set_number':set_number}
        c.execute(sql_statement,parameters)
        
    conn.commit()
    conn.close()
        
    return week_number


# Function that can delete an entire workout, exercise, or a set based on user input; returns week number 
# for use with the function responsible for updating the WeeklyMuscleSets table.

def delete():
    conn = sqlite3.connect('LiftAppTest42.db')
    c = conn.cursor()
    
    delete_query = input('''Do you want to delete a workout, an exercise from a workout, 
                            or a specific set from a workout? (workout, exercise, set) ''').strip().lower()
    while delete_query not in ('workout','exercise','set'):
        delete_query = input('''Do you want to delete a workout, an exercise from a workout, 
                                or a specific set from a workout? (workout, exercise, set) ''').strip().lower()
        
    date = input("Please specify the workout date. YYYY-MM-DD ")
    week_number = int(datetime.strptime(date,'%Y-%m-%d').strftime('%V'))
    
    if delete_query == 'workout':
        
        sql_statement = 'DELETE FROM WorkoutTable WHERE Date=(:date);'
        c.execute(sql_statement,{'date':date})
        
    elif delete_query == 'exercise':
        exercise = input("Please specify the exercise you wish to delete. ")
        
        sql_statement = 'DELETE FROM WorkoutTable WHERE Date=(:date) AND Exercise=(:exercise);'
        c.execute(sql_statement,{'date':date,'exercise':exercise})
        
    else:
        exercise = input("Please specify the exercise from the workout. ")
        set_number = int(input("Please specify the set number you wish to delete. "))
        
        sql_statement = '''DELETE FROM WorkoutTable 
                            WHERE Date=(:date) AND Exercise=(:exercise) AND SetNumber=(:set_number);'''
        c.execute(sql_statement,{'date':date,'exercise':exercise,'set_number':set_number})
        
    conn.commit()
    conn.close()
        
    return week_number


# Updates WeeklyMuscleSets after user updates reps and weight.
def full_update():
    week_number = update_reps_and_weight()
    
    specific_weekly_muscle_sets_update_sql(week_number)
    
# Updates WeeklyMuscleSets after user deletes a workout, exercise, or set.
def full_delete():
    week_number = delete()
    
    specific_weekly_muscle_sets_update_sql(week_number)

