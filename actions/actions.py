# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
import collections

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import sqlite3
import random
from fuzzywuzzy import process

class QueryObligationType(Action):

    def name(self) -> Text:
        return "query_obligation_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Runs a query using only the type column, fuzzy matching against the
        obligation_type slot. Outputs an utterance to the user w/ the relevent 
        information for one of the returned rows.
        """
        conn_obligations = create_connection_obligations(self, db_file="../primavera_db/obligationsDB")

        slot_value = tracker.get_slot("obligation_type")
        slot_name = "ID"
        
        # adding fuzzy matching, fingers crossed
        slot_value = DbQueryingMethods.get_closest_value(conn=conn_obligations,
            slot_name=slot_name,slot_value=slot_value)[0]

        get_query_results = DbQueryingMethods.select_by_slot(conn=conn_obligations,
            slot_name=slot_name,slot_value=slot_value)
        return_text = DbQueryingMethods.rows_info_as_text(get_query_results)
        dispatcher.utter_message(text=str(return_text))

        return 

class QueryInsightType(Action):

    def name(self) -> Text:
        return "query_insight_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Runs a query using only the type column, fuzzy matching against the
        obligation_type slot. Outputs an utterance to the user w/ the relevent 
        information for one of the returned rows.
        """
        conn_insights = create_connection_insights(self, db_file="../primavera_db/insightsDB")

        slot_value = tracker.get_slot("insight_type")
        slot_name = "ID"
        
        # adding fuzzy matching, fingers crossed
        slot_value = DbQueryingMethods.get_closest_value(conn=conn_insights,
            slot_name=slot_name,slot_value=slot_value)[0]

        get_query_results = DbQueryingMethods.select_by_slot(conn=conn_insights,
            slot_name=slot_name,slot_value=slot_value)
        return_text = DbQueryingMethods.rows_info_as_text(get_query_results)
        dispatcher.utter_message(text=str(return_text))

        return 

class QueryObligation(Action):

    def name(self) -> Text:
        return "query_obligation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """
        Runs a query using both the value_to_pay & type columns (fuzzy matching against the
        relevent slots). Finds a match for both if possible, otherwise a match for the
        type only, value_to_pay only in that order. Output is an utterance directly to the
        user with a randomly selected matching row.
        """
        conn_obligations = DbQueryingMethods.create_connection_obligations(db_file="./primavera_db/obligationsDB")

        # get matching entries for obligation type
        obligation_type_value = tracker.get_slot("obligation_type")
        print("obligation_type_value1:", obligation_type_value)
        # make sure we don't pass None to our fuzzy matcher
        if obligation_type_value == None:
            obligation_type_value = " "
        obligation_type_name = "TYPE"
        obligation_type_value = DbQueryingMethods.get_closest_value_obligations(conn_obligations=conn_obligations,
            slot_name=obligation_type_name,slot_value=obligation_type_value)[0]
        print("obligation_type_value2:", obligation_type_value)
        query_results = DbQueryingMethods.select_by_slot_obligations(conn_obligations=conn_obligations,
            slot_name=obligation_type_name,slot_value=obligation_type_value)

        '''
        # intersection of two queries
        value_to_pay_set = collections.Counter(query_results_value_to_pay)
        type_set =  collections.Counter(query_results_type)

        query_results_overlap = list((value_to_pay_set & type_set).elements())

        # apology for not having the right info
        apology = "I couldn't find exactly what you wanted, but you might like this."

        # return info for both, or value_to_pay match or type match or nothing
        if len(query_results_overlap)>0:
            return_text = DbQueryingMethods.rows_info_as_text(query_results_overlap)
        elif len(list(query_results_value_to_pay))>0:
            return_text = apology + DbQueryingMethods.rows_info_as_text(query_results_value_to_pay)
        elif len(list(query_results_type))>0:
            return_text = apology + DbQueryingMethods.rows_info_as_text(query_results_type)
        else:
            return_text = DbQueryingMethods.rows_info_as_text(query_results_overlap)
        '''

        return_text = DbQueryingMethods.rows_info_as_text_obligations(query_results)
        
        # print results for user
        dispatcher.utter_message(text=str(return_text))

        return

class QueryInsight(Action):

    def name(self) -> Text:
        return "query_insight"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """
        Runs a query using both the message & type columns (fuzzy matching against the
        relevent slots). Finds a match for both if possible, otherwise a match for the
        type only, messages only in that order. Output is an utterance directly to the
        user with a randomly selected matching row.
        """
        conn_insights = DbQueryingMethods.create_connection_insights(db_file="./primavera_db/insightsDB")

        # get matching entries for obligation type
        insight_type_value = tracker.get_slot("insight_type")
        print("insight_type_value1:", insight_type_value)
        # make sure we don't pass None to our fuzzy matcher
        if insight_type_value == None:
            insight_type_value = " "
        insight_type_name = "TYPE"
        insight_type_value = DbQueryingMethods.get_closest_value_insights(conn_insights=conn_insights,
            slot_name=insight_type_name,slot_value=insight_type_value)[0]
        print("insight_type_value2:", insight_type_value)
        query_results = DbQueryingMethods.select_by_slot_insights(conn_insights=conn_insights,
            slot_name=insight_type_name,slot_value=insight_type_value)

        return_text = DbQueryingMethods.rows_info_as_text_insights(query_results)
        
        # print results for user
        dispatcher.utter_message(text=str(return_text))

        return 

class DbQueryingMethods:
    def create_connection_obligations(db_file):
        """ 
        create a database connection to the SQLite database
        specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn_obligations = None
        try:
            conn_obligations = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn_obligations


    def create_connection_insights(db_file):
        """ 
        create a database connection to the SQLite database
        specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn_insights = None
        try:
            conn_insights = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn_insights

    def get_closest_value_obligations(conn_obligations, slot_name, slot_value):
        """ Given a database column & text input, find the closest 
        match for the input in the column.
        """
        # get a list of all distinct values from our target column
        fuzzy_match_cur_obligations = conn_obligations.cursor()
        fuzzy_match_cur_obligations.execute(f"""SELECT DISTINCT {slot_name} 
                                FROM dataObligations""")
        column_values_obligations = fuzzy_match_cur_obligations.fetchall()

        top_match_obligations = process.extractOne(slot_value, column_values_obligations)

        return(top_match_obligations[0])

    def get_closest_value_insights(conn_insights, slot_name, slot_value):
        """ Given a database column & text input, find the closest 
        match for the input in the column.
        """
        # get a list of all distinct values from our target column
        fuzzy_match_cur_insights = conn_insights.cursor()
        fuzzy_match_cur_insights.execute(f"""SELECT DISTINCT {slot_name} 
                                FROM dataInsights""")
        column_values_insights = fuzzy_match_cur_insights.fetchall()

        top_match_insights = process.extractOne(slot_value, column_values_insights)

        return(top_match_insights[0])

    # slot_name is column
    def select_by_slot_obligations(conn_obligations, slot_name, slot_value):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        cur_obligations = conn_obligations.cursor()
        cur_obligations.execute(f'''SELECT * FROM dataObligations
                    WHERE {slot_name}="{slot_value}"''')

        # return an array
        rows_obligations = cur_obligations.fetchall()

        return(rows_obligations)

    def select_by_slot_insights(conn_insights, slot_name, slot_value):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        cur_insights = conn_insights.cursor()
        cur_insights.execute(f'''SELECT * FROM dataInsights
                    WHERE {slot_name}="{slot_value}"''')

        # return an array
        rows_insights = cur_insights.fetchall()

        return(rows_insights)

    def rows_info_as_text_obligations(rows):
        """
        Return one of the rows (randomly sele cted) passed in 
        as a human-readable text. If there are no rows, returns
        text to that effect.
        """
        if len(list(rows)) < 1:
            return "There are no obligations matching your query."
        else:
            for row in random.sample(rows, 1):
                return f"Your {row[2]} value to pay is {row[3]}€"

    def rows_info_as_text_insights(rows):
        """
        Return one of the rows (randomly sele cted) passed in 
        as a human-readable text. If there are no rows, returns
        text to that effect.
        """
        if len(list(rows)) < 1:
            return "There are no obligations matching your query."
        else:
            for row in random.sample(rows, 1):
                return f"{row[3]}"
