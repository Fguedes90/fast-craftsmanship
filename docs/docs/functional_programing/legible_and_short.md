1️⃣ **Evite mutações de estado.** Retorne novos valores em vez de modificar variáveis existentes.  
2️⃣ **Quebre funções grandes.** Divida lógica complexa em funções pequenas e reutilizáveis.  
3️⃣ **Use funções nomeadas.** Evite lambdas inline em favor de funções nomeadas para maior clareza.  
4️⃣ **Mantenha a tipagem explícita.** Use anotações de tipo para facilitar a leitura e evitar erros.  
5️⃣ **Encadeie operações de forma clara.** Use `pipe()`, `map()`, `filter()` e `reduce()` para evitar aninhamento.  
6️⃣ **Faça código idempotente.** Garanta que funções sempre retornem o mesmo resultado para os mesmos argumentos.  
7️⃣ **Evite efeitos colaterais.** Não altere variáveis externas ou estados globais.  
8️⃣ **Priorize a imutabilidade.** Use estruturas de dados imutáveis sempre que possível.  
9️⃣ **Escreva testes pequenos e focados.** Teste funções isoladas, cobrindo diferentes cenários.  
🔟 **Prefira a simplicidade.** Escreva código claro e direto, evitando truques complicados.  
1️⃣1️⃣ **Trate erros de forma explícita.** Use tipos como `Result` ou `Option` para representar falhas.  
1️⃣2️⃣ **Evite loops imperativos.** Substitua `for` e `while` por funções como `map()`, `filter()` e `reduce()`.  
1️⃣3️⃣ **Use recursão quando apropriado.** Prefira recursão em vez de loops mutáveis.  
1️⃣4️⃣ **Implemente padrões funcionais.** Aplique currying, composição e funções puras.  
1️⃣5️⃣ **Centralize a transformação de dados.** Realize transformações no início do fluxo de dados.  
1️⃣6️⃣ **Evite dependência de estados globais.** Mantenha o estado controlado e limitado.  
1️⃣7️⃣ **Seja consistente com a nomenclatura.** Use nomes claros e consistentes para funções e variáveis.  
1️⃣8️⃣ **Use pattern matching.** Utilize correspondência de padrões para manipular dados complexos.  
1️⃣9️⃣ **Controle os efeitos colaterais.** Realize efeitos colaterais no final do fluxo de dados.  
2️⃣0️⃣ **Documente transformações complexas.** Explique funções e transformações complexas claramente.  
2️⃣1️⃣ **Nunca declare funções lambdas aninhadas ou como argumento para outras funções.** Sempre atribua lambdas a variáveis e use essas variáveis nas funções.