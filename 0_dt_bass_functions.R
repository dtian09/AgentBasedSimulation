# Define the Bass diffusion model function
bass_diffusion <- function(t, p, q, m) {
  #output the prevalence of e-cigarette at t
  adopters <- m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))
  return(adopters)
}

bass_diffusion_decline <- function(t, p, q, m,d) {
  m <- m * exp(-d * t)
  adopters <- m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))
  return(adopters)
}

# Define a function to fit the Bass diffusion model to observed adoption data
fit_bass <- function(data,prop) {
  # Initial guess for parameters
  # Estimate the parameters (p and q)
  # Specify starting values closer to the expected values
  start_values <- list(p = 0.01, q = 0.001)
  
  prop <- ifelse(data$cohort[1]=="1991+" & data$smokstat=="Never smoked", prop, 0)
  
  data$ecig_prevalence <- ifelse(data$cohort=="1991+" & data$smokstat=="Never smoked", data$allecig, data$ecig_prevalence)
  
  # Fit the model using nls
  fit <- nlsLM(ecig_prevalence ~ bass_diffusion(data$quarter, p, q, max(data$ecig_prevalence)+prop), 
             data = data, 
             start = start_values,
             lower=c(p=0,q=0),
             algorithm = "port",  # Try different algorithms if needed
             control = list(maxiter = 1024))  # Increase max iterations if needed
  
  # Assess the fit
  summary(fit)
  model <- summary(fit)
  m_parameter <- ifelse(data$cat=="Never smoked1991+", max(data$allecig)+prop, max(data$ecig_prevalence))
  
  parameters <- data.frame(cohort=unique(data$cohort), smokstat=unique(data$smokstat),
                           p=model$parameters[1], q=model$parameters[2], m=m_parameter)  
  return(parameters)
}


fit_bass_decline <- function(data) {
  # Initial guess for parameters
  # Estimate the parameters (p and q)
  # Specify starting values closer to the expected values
  start_values <- list(p = 0.01, q = 0.001, d=0.01)
  
  # Fit the model using nls
  fit <- nlsLM(ecig_prevalence ~ bass_diffusion_decline(data$quarter, p, q, max(data$ecig_prevalence)*1, d), 
               data = data, 
               start = start_values,
               lower=c(p=0,q=0,d=0),
               algorithm = "port",  # Try different algorithms if needed
               control = list(maxiter = 1024))  # Increase max iterations if needed
  
  # Assess the fit
  summary(fit)
  model <- summary(fit)
  parameters <- data.frame(cohort=unique(data$cohort), smokstat=unique(data$smokstat),
                           p=model$parameters[1], q=model$parameters[2], m=max(data$ecig_prevalence)*1,
                           d=model$parameters[3])  
  return(parameters)
}

# function to generate the combined curve
generate_combined_curve <- function(quarters, p1, q1, m1, d1, p2, q2, m2, d2){
  adopters <- numeric(length(quarters))
  
  for (i in 1:length(quarters)) {
    if(is.na(p2)){
      adopters[i] <- bass_diffusion_decline(quarters[i], p1, q1, m1, d1)
    } else if(is.na(p1) & quarters[i] >= 43){
      adopters[i] <- bass_diffusion_decline(quarters[i] - 43, p2, q2, m2, d2)
    } else if (quarters[i] < 44) {
      adopters[i] <- bass_diffusion_decline(quarters[i], p1, q1, m1, d1)
    } else {
      adopters[i] <- bass_diffusion_decline(quarters[i], p1, q1, m1, d1) +
        bass_diffusion_decline(quarters[i] - 43, p2, q2, m2, d2)
    }
  }
  return(adopters)
}
