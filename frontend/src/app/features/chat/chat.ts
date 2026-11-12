import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { ApiService } from '../../core/services/api';
import { Source } from '../../core/models/chat.model';
import { marked } from 'marked';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat {

  question: string = '';
  messages: ChatMessage[] = [];
  loading: boolean = false;
  error: string = '';
  quickQuestions = [
    'Quelles sont les dates limites pour le dépôt du PFE ?',
    'Où trouver les conventions de stage ?',
    'Comment valider mon semestre ?'
  ];

  formatMessage(content: string): SafeHtml {
    const html = marked.parse(content, { async: false });
    return this.sanitizer.bypassSecurityTrustHtml(html);
}

  constructor(
  private apiService: ApiService,
  private cdr: ChangeDetectorRef,
  private sanitizer: DomSanitizer
) {}

askSuggestedQuestion(question: string): void {
  this.question = question;
  this.sendMessage();
}

sendMessage(): void {

    const question = this.question.trim();

    if (!question || this.loading) {
      return;
    }

    this.messages.push({
      role: 'user',
      content: question
    });

    this.question = '';
    this.loading = true;
    this.error = '';

    this.apiService.askQuestion(question)
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe({
        next: (response) => {

          const citedNumbers = [
  ...response.answer.matchAll(/\[(\d+)\]/g)
].map(match => Number(match[1]));

const citedSources = response.sources.filter(source => {
  const number = Number(source.citation.replace(/\D/g, ''));
  return citedNumbers.includes(number);
});

this.messages.push({
  role: 'assistant',
  content: response.answer,
  sources: citedSources
});

          this.cdr.markForCheck();
        },

        error: (err) => {
          console.error('Erreur API :', err);

          this.error = 'Impossible de contacter le serveur. Vérifiez que le backend est démarré.';

          this.cdr.markForCheck();
        }
      });
  }
}