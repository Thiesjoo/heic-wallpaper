import type { UserFromAPI } from "@/utils/types";
import oidc from "./oidc";

export interface AuthMethod {
  getURLToShowUser(): string;

  getUser: (fullRefresh?: boolean) => Promise<UserFromAPI | null>;
  getToken: () => Promise<string | null>;

  logout: () => Promise<void>;

  registerCallbacks: (
    signedInCallback: (user: UserFromAPI) => void,
    signedOutCallback: () => void,
  ) => void;

  startAuthentication: () => Promise<void> | void;
}

export default oidc satisfies AuthMethod;
