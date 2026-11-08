import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { AskRequest, AskResponse } from '../models/chat.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  // Poser une question au RAG
  askQuestion(question: string, topK: number = 5): Observable<AskResponse> {

    const body: AskRequest = {
      question: question,
      top_k: topK,
      strategy: 'structural'
    };

    return this.http.post<AskResponse>(`${this.apiUrl}/ask`, body);
  }

  // Rechercher dans les documents
  searchDocuments(question: string, topK: number = 5): Observable<any> {

    const body = {
      question: question,
      top_k: topK,
      strategy: 'structural',
      document_type: null
    };

    return this.http.post<any>(`${this.apiUrl}/search`, body);
  }

  // Récupérer les documents
  getDocuments(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/documents`);
  }

  // Vérifier l'état du backend
  checkHealth(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/health`);
  }
}