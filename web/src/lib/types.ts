export type Establishment = {
  id: string;
  source: string;
  source_id: string | null;
  name: string;
  category: string;
  sub_categories: string[] | null;
  address: string | null;
  city: string | null;
  state: string | null;
  postal_code: string | null;
  country: string;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  website: string | null;
  generic_email: string | null;
  generic_email_status: string | null;
  generic_email_verified_at: string | null;
  rating: number | null;
  review_count: number | null;
  amenities: Record<string, unknown> | null;
  enrichment_status: string;
  scraped_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Contact = {
  id: string;
  establishment_id: string;
  full_name: string | null;
  first_name: string | null;
  last_name: string | null;
  role: string | null;
  nominative_email: string | null;
  linkedin_url: string | null;
  email_status: string;
  email_verified_at: string | null;
  source_provider: string | null;
  confidence_score: number | null;
  legal_basis: string | null;
  gdpr_info_sent_at: string | null;
  opt_out_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ContactLite = Pick<
  Contact,
  | "email_status"
  | "nominative_email"
  | "full_name"
  | "role"
  | "source_provider"
>;

export type EstablishmentWithContacts = Establishment & {
  contacts: ContactLite[];
};
