const BASE_URL = "http://localhost:5000/api";

export async function fetchChain() {
  return fetch(`${BASE_URL}/chain`).then(res => res.json());
}

export async function fetchValidation() {
  return fetch(`${BASE_URL}/validate`).then(res => res.json());
}

export async function fetchPagedChain(page = 1, size = 5) {
  return fetch(
    `http://localhost:5000/api/chain/paged?page=${page}&size=${size}`
  ).then(res => res.json());
}