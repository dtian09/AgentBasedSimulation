from typing import Dict
from abc import abstractmethod
import numpy as np
import math
import random
import sys
import pandas as pd

from config.definitions import AgentState, AgentBehaviour, eCigDiffSubGroup
from mbssm.theory import Theory
from mbssm.micro_agent import MicroAgent
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.attribute import Level2AttributeInt, Level2AttributeFloat, Level1Attribute


class COMBTheory(Theory):

    def __init__(self, name, smoking_model: SmokingModel, indx_of_agent: int):
        super().__init__(name)
        self.smoking_model = smoking_model
        self.comp_c: Level1Attribute
        self.comp_o: Level1Attribute
        self.comp_m: Level1Attribute
        self.level2_attributes: Dict = {}  # a hashmap with keys=level 2 attribute names, values=Level2Attribute objects
        self.power = 0  # power within logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        self.indx_of_agent = indx_of_agent
        self.store_level2_attributes_into_map(indx_of_agent)

    def store_level2_attributes_into_map(self, indx_of_agent: int):
        """store the level 2 attributes of agent i from data dataframe of smoking model class into a map
        <l2AttributeName : string, object : Level2Attribute>
        """
        for level2_attribute_name in self.smoking_model.level2_attributes_names:
            if np.isnan(self.smoking_model.data.at[indx_of_agent, level2_attribute_name]):
                # level 2 attribute has NaN (missing value)
                # ignore this level 2 attribute by set it to 0 so that 0*beta=0 in the COMB formula.
                at_obj = Level2AttributeInt(name=level2_attribute_name, value=0)
                self.level2_attributes[level2_attribute_name] = at_obj
            elif level2_attribute_name == 'mUseofNRT':
                agent=self.smoking_model.context.agent((indx_of_agent, self.smoking_model.type, self.smoking_model.rank))
                if agent.pOverCounterNRT.get_value()==1 or agent.pPrescriptionNRT.get_value()==1:
                  val = 1
                else:
                  val = 0 
                at_obj = Level2AttributeInt(name=level2_attribute_name, value=val)
                self.level2_attributes[level2_attribute_name] = at_obj
            elif type(self.smoking_model.data.at[indx_of_agent, level2_attribute_name]) is np.int64:
                at_obj = Level2AttributeInt(name=level2_attribute_name,
                                            value=self.smoking_model.data.at[indx_of_agent, level2_attribute_name])
                self.level2_attributes[level2_attribute_name] = at_obj
            elif type(self.smoking_model.data.at[indx_of_agent, level2_attribute_name]) is np.float64:
                at_obj = Level2AttributeFloat(name=level2_attribute_name,
                                              value=self.smoking_model.data.at[indx_of_agent, level2_attribute_name])
                self.level2_attributes[level2_attribute_name] = at_obj
            else:
                sstr = ' is not int64 or float64 and not stored into the level2_attributes hashmap.'
                sys.exit(str(self.smoking_model.data.at[indx_of_agent, level2_attribute_name]) + sstr)            
        if self.level2_attributes['mSmokerIdentity'].get_value()==2: #mSmokerIdentity: ‘1=I think of myself as a non-smoker’, ‘2=I still think of myself as a smoker’, -1=’don’t know’, 4=’not stated’. 
            at_obj = Level2AttributeInt(name='mNonSmokerSelfIdentity', value=0)
            self.level2_attributes['mNonSmokerSelfIdentity']=at_obj
        elif self.level2_attributes['mSmokerIdentity'].get_value()==1:
            at_obj = Level2AttributeInt(name='mNonSmokerSelfIdentity', value=1)
            self.level2_attributes['mNonSmokerSelfIdentity']=at_obj
        else:
            at_obj = Level2AttributeInt(name='mNonSmokerSelfIdentity', value=self.level2_attributes['mSmokerIdentity'].get_value()) #-1=’don’t know’ or 4=’not stated’.
            self.level2_attributes['mNonSmokerSelfIdentity']=at_obj 

    @abstractmethod
    def do_situation(self, agent: MicroAgent):  # run the situation mechanism of the agent of this theory
        pass

    @abstractmethod
    def make_comp_c(self):
        pass

    @abstractmethod
    def make_comp_o(self):
        pass

    @abstractmethod
    def make_comp_m(self):
        pass

    @abstractmethod
    def do_behaviour(self, agent: MicroAgent):
        """calculate probability of a behaviour using a logistic regression:
        1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)"""
        pass

    @abstractmethod
    def do_learning(self):
        pass

    def do_action(self, agent: MicroAgent):
        """run the action mechanism of the agent of this theory"""
        self.make_comp_c()
        self.make_comp_o()
        self.make_comp_m()
        self.do_behaviour(agent)
      

class RegSmokeTheory(COMBTheory):

    def __init__(self, name, smoking_model: SmokingModel, indx_of_agent: int):
        super().__init__(name, smoking_model, indx_of_agent)

    def do_situation(self, agent: MicroAgent):        
        self.smoking_model.allocateDiffusionToAgent(agent)#change this agent to an ecig user
        if self.smoking_model.months_counter == 12:
            agent.update_difficulty_of_access()
        #update values of the exogenous dynamic attributes and dynamic COM attributes of this agent
        #pPrescriptionNRT
        #pVareniclineUse
        #bCigConsumption
        #oRecieptGPAdvice
        #oPrevalenceOfSmokingInGeographicLocality
        prev=self.smoking_model.geographicSmokingPrevalence.getRegionalPrevalence(self.smoking_model.formatted_month, agent.pRegion)
        at_obj = Level2AttributeInt(name='oPrevalenceOfSmokingInGeographicLocality', value=float(prev))
        self.level2_attributes['oPrevalenceOfSmokingInGeographicLocality'] = at_obj 

    def do_learning(self):
        pass

    def make_comp_c(self):
        if self.smoking_model.uptake_betas.get('C') is not None:
            self.comp_c = Level1Attribute('C')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_uptake_formula['C']:
                self.comp_c.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.uptake_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_c.set_value(val)
            self.power += val * self.smoking_model.uptake_betas.get('C')
        return self.power

    def make_comp_o(self):
        if self.smoking_model.uptake_betas.get('O') is not None:
            self.comp_o = Level1Attribute('O')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_uptake_formula['O']:
                self.comp_o.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.uptake_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_o.set_value(val)
            self.power += val * self.smoking_model.uptake_betas.get('O')
        return self.power

    def make_comp_m(self):
        if self.smoking_model.uptake_betas.get('M') is not None:
            self.comp_m = Level1Attribute('M')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_uptake_formula['M']:
                self.comp_m.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.uptake_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_m.set_value(val)
            self.power += val * self.smoking_model.uptake_betas.get('M')
        return self.power

    def do_behaviour(self, agent: MicroAgent):
        """
        calculate probability of regular smoking uptake using the COMB formula:
            prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias)
        """
        self.power += self.smoking_model.uptake_betas['bias']
        self.power = -1 * self.power
        self.prob_behaviour = 1 / (1 + math.e ** self.power)
        # for a never smoker, run the regular smoking theory to calculate the probability of regular smoking;
        # if p >= threshold {A transitions to a smoker at t+1} else { A stays as never smoker or ex-smoker at t+1}
        self.threshold = random.uniform(0, 1)  # threshold
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.UPTAKE)
            agent.set_state_of_next_time_step(AgentState.SMOKER)
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.NOUPTAKE)
            agent.set_state_of_next_time_step(AgentState.NEVERSMOKE)
        
class QuitAttemptTheory(COMBTheory):

    def __init__(self, name, smoking_model: SmokingModel, indx_of_agent: int):
        super().__init__(name, smoking_model, indx_of_agent)

    def do_situation(self, agent: MicroAgent):
        '''
        Argument: agent (the agent object of this QuitAttemptTheory object)
        
        Change this agent to an e-cigarette user
        Update the dynamic personal characteristics and the dynamic Level 2 attributes of the agent's Quit Attempt Theory
        '''
        self.smoking_model.allocateDiffusionToAgent(agent)#change this agent to an ecig user        
        #update values of the exogenous dynamic attributes and dynamic COM attributes of this agent
        #pPrescriptionNRT
        #pVareniclineUse
        #bCigConsumption
        #mUseofNRT = pOverCounterNRT or pPrescriptionNRT
        agent=self.smoking_model.context.agent((self.indx_of_agent, self.smoking_model.type, self.smoking_model.rank))
        if agent.pOverCounterNRT.get_value()==1 or agent.pPrescriptionNRT.get_value()==1:
           val = 1
        else:
           val = 0
        self.level2_attributes['mUseofNRT'].set_value(val)
        #update oPrevalenceOfSmokingInGeographicLocality
        prev=self.smoking_model.geographicSmokingPrevalence.getRegionalPrevalence(self.smoking_model.formatted_month, agent.pRegion)
        at_obj = Level2AttributeInt(name='oPrevalenceOfSmokingInGeographicLocality', value=float(prev))
        self.level2_attributes['oPrevalenceOfSmokingInGeographicLocality'] = at_obj 
        #oReceiptOfGPAdvice        
        matched_row = self.smoking_model.attempt_exogenous_dynamics_data[
                                (self.smoking_model.attempt_exogenous_dynamics_data["year"] == self.smoking_model.year_of_current_time_step) &
                                (self.smoking_model.attempt_exogenous_dynamics_data["age"] == agent.p_age.get_value()) &
                                (self.smoking_model.attempt_exogenous_dynamics_data["sex"] == agent.p_gender.get_value()) &
                                (self.smoking_model.attempt_exogenous_dynamics_data["social grade"] == agent.p_sep.get_value())
                                ]
        matched_row = pd.DataFrame(matched_row)
        #ipdb.set_trace()#debug break point
        if len(matched_row) > 0:
             col_index = matched_row.columns.get_loc("oReceiptGPAdviceLodOdds")
             logodds = float(matched_row.iat[0, col_index])
             col_index2 = matched_row.columns.get_loc("pNRTLogOdds")
             logodds2 = float(matched_row.iat[0, col_index2])
        else: 
             logodds = 0
             logodds2 = 0
             print(f'Logodds in QuitAttemptTheory are set to 0, no matching logodds for year={self.smoking_model.attempt_exogenous_dynamics_data["year"]},\
                   age={self.smoking_model.attempt_exogenous_dynamics_data["age"]},\
                   sex={self.smoking_model.attempt_exogenous_dynamics_data["sex"]},\
                  social grade={self.smoking_model.attempt_exogenous_dynamics_data["social grade"]}')   
        #sample a value (1 or 0) for oReceiptOfGPAdvice using its logodds and a threshold drawn from uniform distribution [0,1] 
        logodds += agent.propensity_receive_GP_advice_attempt
        prob = math.e ** logodds / (1 + math.e ** logodds)
        threshold = random.uniform(0, 1)
        if prob >= threshold:
           at_obj = Level2AttributeInt(name='oReceiptOfGPAdvice', value=1)
           self.level2_attributes['oReceiptOfGPAdvice'] = at_obj 
        else:
           at_obj = Level2AttributeInt(name='oReceiptOfGPAdvice', value=0)
           self.level2_attributes['oReceiptOfGPAdvice'] = at_obj  
        #sample a value (1 or 0) for pPrescriptionNRT using its logodds and a threshold drawn from uniform distribution [0,1] 
        logodds2 += agent.propensity_NRT_attempt
        prob = math.e ** logodds2 / (1 + math.e ** logodds2)
        threshold = random.uniform(0, 1)
        if prob >= threshold:
           agent.p_prescription_nrt.set_value(1)
        else:
           agent.p_prescription_nrt.set_value(0)  

    def do_learning(self):
        pass

    def make_comp_c(self):
        if self.smoking_model.attempt_betas.get('C') is not None:
            self.comp_c = Level1Attribute('C')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_attempt_formula['C']:
                self.comp_c.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.attempt_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_c.set_value(val)
            self.power += val * self.smoking_model.attempt_betas.get('C')
        return self.power

    def make_comp_o(self):
        if self.smoking_model.attempt_betas.get('O') is not None:
            self.comp_o = Level1Attribute('O')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_attempt_formula['O']:
                self.comp_o.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.attempt_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_o.set_value(val)
            self.power += val * self.smoking_model.attempt_betas.get('O')
        return self.power

    def make_comp_m(self):
        if self.smoking_model.attempt_betas.get('M') is not None:
            self.comp_m = Level1Attribute('M')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_attempt_formula['M']:
                self.comp_m.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.attempt_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_m.set_value(val)
            self.power += val * self.smoking_model.attempt_betas.get('M')
        return self.power

    def do_behaviour(self, agent: MicroAgent):
        """calculate probability of making a quit attempt by using the COMB formula:
        prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias)
        """
        self.power += self.smoking_model.attempt_betas['bias']
        self.power = -1 * self.power
        self.prob_behaviour = 1 / (1 + math.e ** self.power)
        # for a smoker A, run the quit attempt theory to calculate the probability of making a quit attempt.
        # If p >= threshold, { A transitions to a quitter at t+1} else {A stays as a smoker at t+1}
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.QUITATTEMPT)
            agent.set_state_of_next_time_step(state=AgentState.NEWQUITTER)
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.NOQUITEATTEMPT)
            agent.set_state_of_next_time_step(state=AgentState.SMOKER)
        agent.b_number_of_recent_quit_attempts=agent.count_quit_attempt_behaviour()

class QuitMaintenanceTheory(COMBTheory):

    def __init__(self, name, smoking_model: SmokingModel, indx_of_agent: int):
        super().__init__(name, smoking_model, indx_of_agent)

    def do_situation(self, agent: MicroAgent):
        self.smoking_model.allocateDiffusionToAgent(agent)#change this agent to an ecig user
        #update values of the exogenous dynamic attributes and dynamic COM attributes of this agent        
        #pVareniclineUse        
        #bCigConsumption
        #cUseOfBehaviourSupport
        #cCytisineUse
        #update oPrevalenceOfSmokingInGeographicLocality
        prev=self.smoking_model.geographicSmokingPrevalence.getRegionalPrevalence(self.smoking_model.formatted_month, agent.pRegion)
        at_obj = Level2AttributeInt(name='oPrevalenceOfSmokingInGeographicLocality', value=float(prev))
        self.level2_attributes['oPrevalenceOfSmokingInGeographicLocality'] = at_obj 
        if agent.get_current_state()==AgentState.NEWQUITTER:
            #pPrescriptionNRT
            matched_row = self.smoking_model.maintenance_exogenous_dynamics_data[
                                (self.smoking_model.maintenance_exogenous_dynamics_data["year"] == self.smoking_model.year_of_current_time_step) &
                                (self.smoking_model.maintenance_exogenous_dynamics_data["age"] == agent.p_age.get_value()) &
                                (self.smoking_model.maintenance_exogenous_dynamics_data["sex"] == agent.p_gender.get_value()) &
                                (self.smoking_model.maintenance_exogenous_dynamics_data["social grade"] == agent.p_sep.get_value())
                                ]
            matched_row = pd.DataFrame(matched_row)
            #ipdb.set_trace()#debug break point
            if len(matched_row) > 0:
                col_index = matched_row.columns.get_loc("pPrescriptionNRTLogOdds")
                logodds = float(matched_row.iat[0, col_index])
                col_index2 = matched_row.columns.get_loc("cUseOfBehaviourSupportLogOdds")
                logodds2 = float(matched_row.iat[0, col_index2])
                col_index3 = matched_row.columns.get_loc("pVareniclineUseLogOdds")
                logodds3 = float(matched_row.iat[0, col_index3])             
            else: 
                logodds = 0
                logodds2 = 0
                logodds3 = 0
                print(f'Logodds in QuitMaintenanceTheory are set to 0, no matching logodds for year={self.smoking_model.attempt_exogenous_dynamics_data["year"]},\
                    age={self.smoking_model.attempt_exogenous_dynamics_data["age"]},\
                    sex={self.smoking_model.attempt_exogenous_dynamics_data["sex"]},\
                    social grade={self.smoking_model.attempt_exogenous_dynamics_data["social grade"]}')   
            #update p_prescription_nrt
            logodds += agent.propensity_NRT_maintenance   
            prob = math.e ** logodds / (1 + math.e ** logodds)
            threshold = random.uniform(0, 1)
            if prob >= threshold:
                agent.p_prescription_nrt.set_value(1)
            else:
                agent.p_prescription_nrt.set_value(0)
            #update cUseOfBehaviourSupport
            logodds2 += agent.propensity_behaviour_support_maintenance
            prob = math.e ** logodds2 / (1 + math.e ** logodds2)
            threshold = random.uniform(0, 1)     
            if prob >= threshold:
                at_obj = Level2AttributeInt(name='', value=1)
                self.level2_attributes['cUseOfBehaviourSupport'] = at_obj 
            else:
                at_obj = Level2AttributeInt(name='cUseOfBehaviourSupport', value=0)
                self.level2_attributes['cUseOfBehaviourSupport'] = at_obj  
            #update p_varenicline_use
            logodds3 += agent.propensity_varenicline_maintenance
            prob = math.e ** logodds3 / (1 + math.e ** logodds3)
            threshold = random.uniform(0, 1)
            if prob >= threshold:
                agent.p_varenicline_use.set_value(1)
            else:
                agent.p_varenicline_use.set_value(0)
            
        



    def do_learning(self):
        pass

    def make_comp_c(self):
        if self.smoking_model.success_betas.get('C') is not None:
            self.comp_c = Level1Attribute('C')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_success_formula['C']:
                self.comp_c.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.success_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_c.set_value(val)
            self.power += val * self.smoking_model.success_betas.get('C')
        return self.power

    def make_comp_o(self):
        if self.smoking_model.success_betas.get('O') is not None:
            self.comp_o = Level1Attribute('O')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_success_formula['O']:
                self.comp_o.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.success_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_o.set_value(val)
            self.power += val * self.smoking_model.success_betas.get('O')
        return self.power

    def make_comp_m(self):
        if self.smoking_model.success_betas.get('M') is not None:
            self.comp_m = Level1Attribute('M')
            val = 0
            for level2_attribute_name in self.smoking_model.level2_attributes_of_success_formula['M']:
                self.comp_m.add_level2_attribute(self.level2_attributes[level2_attribute_name])
                beta = self.smoking_model.success_betas[level2_attribute_name]
                val += beta * self.level2_attributes[level2_attribute_name].get_value()
            self.comp_m.set_value(val)
            self.power += val * self.smoking_model.success_betas.get('M')
        return self.power

    def do_behaviour(self, agent: MicroAgent):
        """calculate probability of quit success by using the COMB formula:
        prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias)"""
        self.power += self.smoking_model.success_betas['bias']
        self.power = -1 * self.power
        self.prob_behaviour = 1 / (1 + math.e ** self.power)
        # for a quitter A,
        #  run the quit success theory to calculate the probability of maintaining a quit attempt;
        #  if p >= threshold
        #  {A does quit success behaviour at t;
        #   k=k+1;
        #   if k < 12
        #     {transition to ongoing quitterk;}
        #   else //k==12
        #     {A transitions to an ex-smoker at t+1;
        #      k=0;}
        #  }
        #  else {A performs quit failure behaviour at t and transitions to a smoker at t+1;
        #        k=0;
        #  }
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.QUITMAINTENANCE)
            agent.b_months_since_quit += 1
            #cCigAddictStrength[t+1] = round (cCigAddictStrength[t] * exp(lambda*t)), where lambda = 0.0368 and t = 4 (weeks)
            self.level2_attributes['cCigAddictStrength'].set_value(np.round(self.level2_attributes['cCigAddictStrength'].get_value() * np.exp(self.smoking_model.lbda*self.smoking_model.tickInterval)))
            #sample from prob of smoker self identity = 1/(1+alpha*(k*t)^beta) where alpha = 1.1312, beta = 0.500, k = no. of quit successes and t = 4 (weeks)
            threshold=random.uniform(0,1)
            successCount=agent.behaviour_buffer.count(AgentBehaviour.QUITMAINTENANCE)
            probOfSmokerSelfIdentity=1/(1+self.smoking_model.alpha*(successCount*self.smoking_model.tickInterval)**self.smoking_model.beta)
            if probOfSmokerSelfIdentity >= threshold:
                self.level2_attributes['mSmokerIdentity'].set_value(2) #mSmokerIdentity: ‘1=I think of myself as a non-smoker’, ‘2=I still think of myself as a smoker’, -1=’don’t know’, 4=’not stated’. 
                self.level2_attributes['mNonSmokerSelfIdentity'].set_value(0)
            else:
                self.level2_attributes['mSmokerIdentity'].set_value(1)
                self.level2_attributes['mNonSmokerSelfIdentity'].set_value(1)
            if agent.b_months_since_quit < 12:
                if agent.b_months_since_quit==1:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER1)
                elif agent.b_months_since_quit==2:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER2)
                elif agent.b_months_since_quit==3:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER3)
                elif agent.b_months_since_quit==4:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER4)
                elif agent.b_months_since_quit==5:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER5)
                elif agent.b_months_since_quit==6:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER6)
                elif agent.b_months_since_quit==7:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER7)
                elif agent.b_months_since_quit==8:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER8)
                elif agent.b_months_since_quit==9:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER9)
                elif agent.b_months_since_quit==10:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER10)
                elif agent.b_months_since_quit==11:
                    agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER11)
            else:#b_months_since_quit==12
                agent.set_state_of_next_time_step(AgentState.EXSMOKER)
                agent.b_months_since_quit=0
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.QUITFAILURE)
            agent.set_state_of_next_time_step(AgentState.SMOKER)
            agent.b_months_since_quit = 0
            self.level2_attributes['cCigAddictStrength'].set_value(agent.preQuitAddictionStrength)
        agent.b_number_of_recent_quit_attempts=agent.count_quit_attempt_behaviour()

