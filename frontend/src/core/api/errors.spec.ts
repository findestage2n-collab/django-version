import { AxiosError } from "axios";
import { describe, expect, it } from "vitest";

import { ApiError, toApiError } from "./errors";

describe("toApiError", () => {
  it("traduit l'enveloppe d'erreur du backend", () => {
    const axiosError = new AxiosError("fail");
    axiosError.response = {
      status: 400,
      data: {
        error: { code: "validation_error", message: "Invalide", details: { nom: ["Requis"] } },
        request_id: "abc",
      },
    } as AxiosError["response"];
    const error = toApiError(axiosError);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.code).toBe("validation_error");
    expect(error.fieldErrors()).toEqual({ nom: "Requis" });
    expect(error.requestId).toBe("abc");
  });

  it("signale un serveur injoignable", () => {
    expect(toApiError(new AxiosError("Network Error")).code).toBe("network_error");
  });
});
