"""
The pygad.utils.parent_selection module has all the built-in parent selection operators.
"""

import numpy
from ..helper import nsga2

class ParentSelection:
    def steady_state_selection(self, fitness, num_parents):
    
        """
        Selects the parents using the steady-state selection technique. Later, these parents will mate to produce the offspring.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """

        fitness_sorted = sorted(range(len(fitness)), key=lambda k: fitness[k])
        fitness_sorted.reverse()

        # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)

        for parent_num in range(num_parents):
            parents[parent_num, :] = self.population[fitness_sorted[parent_num], :].copy()

        return parents, numpy.array(fitness_sorted[:num_parents])

    def rank_selection(self, fitness, num_parents):

        """
        Selects the parents using the rank selection technique. Later, these parents will mate to produce the offspring.
        Rank selection gives a rank from 1 to N (number of solutions) to each solution based on its fitness.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """

        # This has the index of each solution in the population.
        fitness_sorted = sorted(range(len(fitness)), key=lambda k: fitness[k])

        # Rank the solutions based on their fitness. The worst is gives the rank 1. The best has the rank N.
        rank = numpy.arange(1, self.sol_per_pop+1)

        probs = rank / numpy.sum(rank)

        probs_start, probs_end, parents = self.wheel_cumulative_probs(probs=probs.copy(), 
                                                                      num_parents=num_parents)

        parents_indices = []

        for parent_num in range(num_parents):
            rand_prob = numpy.random.rand()
            for idx in range(probs.shape[0]):
                if (rand_prob >= probs_start[idx] and rand_prob < probs_end[idx]):
                    # The variable idx has the rank of solution but not its index in the population.
                    # Return the correct index of the solution.
                    mapped_idx = fitness_sorted[idx]
                    parents[parent_num, :] = self.population[mapped_idx, :].copy()
                    parents_indices.append(mapped_idx)
                    break

        return parents, numpy.array(parents_indices)

    def random_selection(self, fitness, num_parents):
    
        """
        Selects the parents randomly. Later, these parents will mate to produce the offspring.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """

        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)

        rand_indices = numpy.random.randint(low=0.0, high=fitness.shape[0], size=num_parents)

        for parent_num in range(num_parents):
            parents[parent_num, :] = self.population[rand_indices[parent_num], :].copy()

        return parents, rand_indices

    def tournament_selection(self, fitness, num_parents):

        """
        Selects the parents using the tournament selection technique. Later, these parents will mate to produce the offspring.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """
    
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)
    
        parents_indices = []
    
        for parent_num in range(num_parents):
            rand_indices = numpy.random.randint(low=0.0, high=len(fitness), size=self.K_tournament)
            K_fitnesses = fitness[rand_indices]
            selected_parent_idx = numpy.where(K_fitnesses == numpy.max(K_fitnesses))[0][0]
            parents_indices.append(rand_indices[selected_parent_idx])
            parents[parent_num, :] = self.population[rand_indices[selected_parent_idx], :].copy()
    
        return parents, numpy.array(parents_indices)
    
    def roulette_wheel_selection(self, fitness, num_parents):
    
        """
        Selects the parents using the roulette wheel selection technique. Later, these parents will mate to produce the offspring.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """
    
        fitness_sum = numpy.sum(fitness)
        if fitness_sum == 0:
            self.logger.error("Cannot proceed because the sum of fitness values is zero. Cannot divide by zero.")
            raise ZeroDivisionError("Cannot proceed because the sum of fitness values is zero. Cannot divide by zero.")

        probs = fitness / fitness_sum

        probs_start, probs_end, parents = self.wheel_cumulative_probs(probs=probs.copy(), 
                                                                      num_parents=num_parents)

        parents_indices = []

        for parent_num in range(num_parents):
            rand_prob = numpy.random.rand()
            for idx in range(probs.shape[0]):
                if (rand_prob >= probs_start[idx] and rand_prob < probs_end[idx]):
                    parents[parent_num, :] = self.population[idx, :].copy()
                    parents_indices.append(idx)
                    break

        return parents, numpy.array(parents_indices)

    def wheel_cumulative_probs(self, probs, num_parents):
        """
        A helper function to calculate the wheel probabilities for these 2 methods:
            1) roulette_wheel_selection
            2) rank_selection
        It accepts a single 1D array representing the probabilities of selecting each solution.
        It returns 2 1D arrays:
            1) probs_start has the start of each range.
            2) probs_start has the end of each range.
        It also returns an empty array for the parents.
        """

        probs_start = numpy.zeros(probs.shape, dtype=float) # An array holding the start values of the ranges of probabilities.
        probs_end = numpy.zeros(probs.shape, dtype=float) # An array holding the end values of the ranges of probabilities.

        curr = 0.0

        # Calculating the probabilities of the solutions to form a roulette wheel.
        for _ in range(probs.shape[0]):
            min_probs_idx = numpy.where(probs == numpy.min(probs))[0][0]
            probs_start[min_probs_idx] = curr
            curr = curr + probs[min_probs_idx]
            probs_end[min_probs_idx] = curr
            probs[min_probs_idx] = 99999999999

        # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)

        return probs_start, probs_end, parents

    def stochastic_universal_selection(self, fitness, num_parents):

        """
        Selects the parents using the stochastic universal selection technique. Later, these parents will mate to produce the offspring.
        It accepts 2 parameters:
            -fitness: The fitness values of the solutions in the current population.
            -num_parents: The number of parents to be selected.
        It returns an array of the selected parents.
        """

        fitness_sum = numpy.sum(fitness)
        if fitness_sum == 0:
            self.logger.error("Cannot proceed because the sum of fitness values is zero. Cannot divide by zero.")
            raise ZeroDivisionError("Cannot proceed because the sum of fitness values is zero. Cannot divide by zero.")
        probs = fitness / fitness_sum
        probs_start = numpy.zeros(probs.shape, dtype=float) # An array holding the start values of the ranges of probabilities.
        probs_end = numpy.zeros(probs.shape, dtype=float) # An array holding the end values of the ranges of probabilities.

        curr = 0.0

        # Calculating the probabilities of the solutions to form a roulette wheel.
        for _ in range(probs.shape[0]):
            min_probs_idx = numpy.where(probs == numpy.min(probs))[0][0]
            probs_start[min_probs_idx] = curr
            curr = curr + probs[min_probs_idx]
            probs_end[min_probs_idx] = curr
            probs[min_probs_idx] = 99999999999

        pointers_distance = 1.0 / self.num_parents_mating # Distance between different pointers.
        first_pointer = numpy.random.uniform(low=0.0, 
                                             high=pointers_distance, 
                                             size=1)[0] # Location of the first pointer.

        # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)

        parents_indices = []

        for parent_num in range(num_parents):
            rand_pointer = first_pointer + parent_num*pointers_distance
            for idx in range(probs.shape[0]):
                if (rand_pointer >= probs_start[idx] and rand_pointer < probs_end[idx]):
                    parents[parent_num, :] = self.population[idx, :].copy()
                    parents_indices.append(idx)
                    break

        return parents, numpy.array(parents_indices)

    def tournament_selection_nsga2(self,
                                   fitness,
                                   num_parents
                                   # pareto_fronts,
                                   # solutions_fronts_indices, 
                                   ):
    
        """
        Select the parents using the tournament selection technique for NSGA-II. 
        The traditional tournament selection uses the fitness values. But the tournament selection for NSGA-II uses non-dominated sorting and crowding distance.
        Using non-dominated sorting, the solutions are distributed across pareto fronts. The fronts are given the indices 0, 1, 2, ..., N where N is the number of pareto fronts. The lower the index of the pareto front, the better its solutions.
        To select the parents solutions, 2 solutions are selected randomly. If the 2 solutions are in different pareto fronts, then the solution comming from a pareto front with lower index is selected.
        If 2 solutions are in the same pareto front, then crowding distance is calculated. The solution with the higher crowding distance is selected.
        If the 2 solutions are in the same pareto front and have the same crowding distance, then a solution is randomly selected.
        Later, the selected parents will mate to produce the offspring.
    
        It accepts 2 parameters:
            -fitness: The fitness values for the current population.
            -num_parents: The number of parents to be selected.
            -pareto_fronts: A nested array of all the pareto fronts. Each front has its solutions.
            -solutions_fronts_indices: A list of the pareto front index of each solution in the current population.
    
        It returns an array of the selected parents alongside their indices in the population.
        """
    
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)
    
        # The indices of the selected parents.
        parents_indices = []
    
        # TODO If there is only a single objective, each pareto front is expected to have only 1 solution.
        # TODO Make a test to check for that behaviour.
        pareto_fronts, solutions_fronts_indices = nsga2.non_dominated_sorting(fitness)
    
        # Randomly generate pairs of indices to apply for NSGA-II tournament selection for selecting the parents solutions.
        rand_indices = numpy.random.randint(low=0.0, 
                                            high=len(solutions_fronts_indices), 
                                            size=(num_parents, self.K_tournament))
        # rand_indices[0, 0] = 5
        # rand_indices[0, 1] = 3
        # rand_indices[1, 0] = 1
        # rand_indices[1, 1] = 6
    
        for parent_num in range(num_parents):
            # Return the indices of the current 2 solutions.
            current_indices = rand_indices[parent_num]
            # Return the front index of the 2 solutions.
            parent_fronts_indices = solutions_fronts_indices[current_indices]
    
            if parent_fronts_indices[0] < parent_fronts_indices[1]:
                # If the first solution is in a lower pareto front than the second, then select it.
                selected_parent_idx = current_indices[0]
            elif parent_fronts_indices[0] > parent_fronts_indices[1]:
                # If the second solution is in a lower pareto front than the first, then select it.
                selected_parent_idx = current_indices[1]
            else:
                # The 2 solutions are in the same pareto front.
                # The selection is made using the crowding distance.
    
                # A list holding the crowding distance of the current 2 solutions. It is initialized to -1.
                solutions_crowding_distance = [-1, -1]
    
                # Fetch the current pareto front.
                pareto_front = pareto_fronts[parent_fronts_indices[0]] # Index 1 can also be used.
    
                # If there is only 1 solution in the pareto front, just return it without calculating the crowding distance (it is useless).
                if pareto_front.shape[0] == 1:
                    selected_parent_idx = current_indices[0] # Index 1 can also be used.
                else:
                    # Reaching here means the pareto front has more than 1 solution.
    
                    # Calculate the crowding distance of the solutions of the pareto front.
                    obj_crowding_distance_list, crowding_distance_sum, crowding_dist_front_sorted_indices, crowding_dist_pop_sorted_indices = nsga2.crowding_distance(pareto_front=pareto_front.copy(),
                                                                                                                                                                      fitness=fitness)
    
                    # This list has the sorted front-based indices for the solutions in the current pareto front.
                    crowding_dist_front_sorted_indices = list(crowding_dist_front_sorted_indices)
                    # This list has the sorted population-based indices for the solutions in the current pareto front.
                    crowding_dist_pop_sorted_indices = list(crowding_dist_pop_sorted_indices)
    
                    # Return the indices of the solutions from the pareto front.
                    solution1_idx = crowding_dist_pop_sorted_indices.index(current_indices[0])
                    solution2_idx = crowding_dist_pop_sorted_indices.index(current_indices[1])
        
                    # Fetch the crowding distance using the indices.
                    solutions_crowding_distance[0] = crowding_distance_sum[solution1_idx][1]
                    solutions_crowding_distance[1] = crowding_distance_sum[solution2_idx][1]
        
                    # # Instead of using the crowding distance, we can select the solution that comes first in the list.
                    # # Its limitation is that it is biased towards the low indexed solution if the 2 solutions have the same crowding distance.
                    # if solution1_idx < solution2_idx:
                    #     # Select the first solution if it has higher crowding distance.
                    #     selected_parent_idx = current_indices[0]
                    # else:
                    #     # Select the second solution if it has higher crowding distance.
                    #     selected_parent_idx = current_indices[1]
        
                    if solutions_crowding_distance[0] > solutions_crowding_distance[1]:
                        # Select the first solution if it has higher crowding distance.
                        selected_parent_idx = current_indices[0]
                    elif solutions_crowding_distance[1] > solutions_crowding_distance[0]:
                        # Select the second solution if it has higher crowding distance.
                        selected_parent_idx = current_indices[1]
                    else:
                        # If the crowding distance is equal, select the parent randomly.
                        rand_num = numpy.random.uniform()
                        if rand_num < 0.5:
                            # If the random number is < 0.5, then select the first solution.
                            selected_parent_idx = current_indices[0]
                        else:
                            # If the random number is >= 0.5, then select the second solution.
                            selected_parent_idx = current_indices[1]
    
            # Insert the selected parent index.
            parents_indices.append(selected_parent_idx)
            # Insert the selected parent.
            parents[parent_num, :] = self.population[selected_parent_idx, :].copy()
    
        # Make sure the parents indices is returned as a NumPy array.
        return parents, numpy.array(parents_indices)
    
    def nsga2_selection(self,
                        fitness,
                        num_parents
                        # pareto_fronts,
                        # solutions_fronts_indices
                        ):
    
        """
        Select the parents using the Non-Dominated Sorting Genetic Algorithm II (NSGA-II). 
        The selection is done using non-dominated sorting and crowding distance.
        Using non-dominated sorting, the solutions are distributed across pareto fronts. The fronts are given the indices 0, 1, 2, ..., N where N is the number of pareto fronts. The lower the index of the pareto front, the better its solutions.
        The parents are selected from the lower pareto fronts and moving up until selecting the number of desired parents. 
        A solution from a pareto front X cannot be taken as a parent until all solutions in pareto front Y is selected given that Y < X.
        For a pareto front X, if only a subset of its solutions is needed, then the corwding distance is used to determine which solutions to be selected from the front. The solution with the higher crowding distance is selected.
        If the 2 solutions are in the same pareto front and have the same crowding distance, then a solution is randomly selected.
        Later, the selected parents will mate to produce the offspring.
    
        It accepts 2 parameters:
            -fitness: The fitness values for the current population.
            -num_parents: The number of parents to be selected.
            -pareto_fronts: A nested array of all the pareto fronts. Each front has its solutions.
            -solutions_fronts_indices: A list of the pareto front index of each solution in the current population.
    
        It returns an array of the selected parents alongside their indices in the population.
        """
    
        if self.gene_type_single == True:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=self.gene_type[0])
        else:
            parents = numpy.empty((num_parents, self.population.shape[1]), dtype=object)
    
        # The indices of the selected parents.
        parents_indices = []
    
        # TODO If there is only a single objective, each pareto front is expected to have only 1 solution.
        # TODO Make a test to check for that behaviour.
        pareto_fronts, solutions_fronts_indices = nsga2.non_dominated_sorting(fitness)

        # The number of remaining parents to be selected.
        num_remaining_parents = num_parents
    
        # A loop variable holding the index of the current pareto front.
        pareto_front_idx = 0
        while num_remaining_parents != 0 and pareto_front_idx < len(pareto_fronts):
            # Return the current pareto front.
            current_pareto_front = pareto_fronts[pareto_front_idx]
            # Check if the entire front fits into the parents array.
            # If so, then insert all the solutions in the current front into the parents array.
            if num_remaining_parents >= len(current_pareto_front):
                for sol_idx in range(len(current_pareto_front)):
                    selected_solution_idx = current_pareto_front[sol_idx, 0]
                    # Insert the parent into the parents array.
                    parents[sol_idx, :] = self.population[selected_solution_idx, :].copy()
                    # Insert the index of the selected parent.
                    parents_indices.append(selected_solution_idx)
    
                # Decrement the number of remaining parents by the length of the pareto front.
                num_remaining_parents -= len(current_pareto_front)
            else:
                # If only a subset of the front is needed, then use the crowding distance to sort the solutions and select only the number needed.
    
                # Calculate the crowding distance of the solutions of the pareto front.
                obj_crowding_distance_list, crowding_distance_sum, crowding_dist_front_sorted_indices, crowding_dist_pop_sorted_indices = nsga2.crowding_distance(pareto_front=current_pareto_front.copy(),
                                                                                                                                                                  fitness=fitness)

                for selected_solution_idx in crowding_dist_pop_sorted_indices[0:num_remaining_parents]:
                    # Insert the parent into the parents array.
                    parents[sol_idx, :] = self.population[selected_solution_idx, :].copy()
                    # Insert the index of the selected parent.
                    parents_indices.append(selected_solution_idx)
    
                # Decrement the number of remaining parents by the number of selected parents.
                num_remaining_parents -= num_remaining_parents
    
            # Increase the pareto front index to take parents from the next front.
            pareto_front_idx += 1
    
        # Make sure the parents indices is returned as a NumPy array.
        return parents, numpy.array(parents_indices)
