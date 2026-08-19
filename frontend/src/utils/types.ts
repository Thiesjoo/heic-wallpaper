export type User = {
  name: {
    first: string;
    last: string;
  };
  email: string;
  settings: UserSettings;
  avatarUrl?: string;
};

export type UserSettings = {
  backgroundURL: string;
  showSeconds: boolean;
  showDate: boolean;
  showVersion: boolean;
  showFavorites: boolean;
  widgetsAvailable: unknown[];
};

export type UserFromAPI = User;
