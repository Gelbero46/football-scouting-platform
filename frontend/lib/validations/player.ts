import * as z from 'zod'

export const playerSchema = z.object({
  // Basic Information
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(255, 'Name must be less than 255 characters'),
  
  full_name: z.string()
    .max(255, 'Full name must be less than 255 characters')
    .optional()
    .or(z.literal('')),
  
  position: z.string()
    .min(1, 'Position is required'),
  
  current_club: z.string()
    .max(255)
    .optional()
    .or(z.literal('')),
  
  nationality: z.string()
    .max(100)
    .optional()
    .or(z.literal('')),
  
  second_nationality: z.string()
    .max(100)
    .optional()
    .or(z.literal('')),
  
  // Date
  date_of_birth: z.string()
    .optional()
    .or(z.literal('')),
  
  // Physical Attributes
  height_cm: z.coerce.number()
    .int()
    .min(150, 'Height must be at least 150cm')
    .max(220, 'Height must be less than 220cm')
    .optional()
    .or(z.literal('')),
  
  weight_kg: z.coerce.number()
    .int()
    .min(50, 'Weight must be at least 50kg')
    .max(120, 'Weight must be less than 120kg')
    .optional()
    .or(z.literal('')),
  
  preferred_foot: z.enum(['left', 'right', 'both', ''])
    .optional(),
  
  // Financial
  market_value_eur: z.coerce.number()
    .int()
    .min(0, 'Market value cannot be negative')
    .optional()
    .or(z.literal('')),
  
  weekly_wage_eur: z.coerce.number()
    .int()
    .min(0, 'Weekly wage cannot be negative')
    .optional()
    .or(z.literal('')),
  
  // Ratings
  overall_rating: z.coerce.number()
    .int()
    .min(0, 'Rating must be between 0 and 100')
    .max(100, 'Rating must be between 0 and 100')
    .optional()
    .or(z.literal('')),
  
  potential_rating: z.coerce.number()
    .int()
    .min(0, 'Potential must be between 0 and 100')
    .max(100, 'Potential must be between 0 and 100')
    .optional()
    .or(z.literal('')),
  
  // Notes
  scouting_notes: z.string()
    .max(5000, 'Notes must be less than 5000 characters')
    .optional()
    .or(z.literal('')),
})

export type PlayerFormValues = z.infer<typeof playerSchema>