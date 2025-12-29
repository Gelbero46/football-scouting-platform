import * as z from 'zod'

export const coachSchema = z.object({
  // Basic Information
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(255, 'Name must be less than 255 characters'),
  
  full_name: z.string()
    .max(255, 'Full name must be less than 255 characters')
    .optional()
    .or(z.literal('')),
  
  current_club: z.string()
    .max(255)
    .optional()
    .or(z.literal('')),
  
  nationality: z.string()
    .max(100)
    .optional()
    .or(z.literal('')),
  
  // Date
  date_of_birth: z.string()
    .optional()
    .or(z.literal('')),
  
  // Coaching Information
  preferred_formation: z.string()
    .min(1, 'Preferred formation is required')
    .max(20),
  
  coaching_level: z.enum(['amateur', 'semi_pro', 'professional', 'elite'])
  .optional(),

  current_role: z.enum(['head_coach', 'assistant', 'youth_coach'])
  .optional(),
  
  years_experience: z.coerce.number()
    .int()
    .min(0, 'Years of experience cannot be negative')
    .max(50, 'Years of experience must be less than 50'),
  
  // Financial
  estimated_salary_eur: z.coerce.number()
    .int()
    .min(0, 'Salary cannot be negative')
    .optional()
    .or(z.literal('')),

  
  // Ratings
  // potential_rating: z.coerce.number()
  //   .int()
  //   .min(0, 'Potential must be between 0 and 100')
  //   .max(100, 'Potential must be between 0 and 100')
  //   .optional()
  //   .or(z.literal('')),

  overall_rating: z.coerce.number()
    .int()
    .min(0, 'Rating must be between 0 and 100')
    .max(100, 'Rating must be between 0 and 100')
    .optional()
    .or(z.literal('')),
  
  // Notes
  scouting_notes: z.string()
    .max(5000, 'Notes must be less than 5000 characters')
    .optional()
    .or(z.literal('')),
})

export type CoachFormValues = z.infer<typeof coachSchema>