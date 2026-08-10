import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1000})
        page = await context.new_page()

        # Listen to console and page errors
        page.on("console", lambda msg: print(f"Browser Console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser Page Error: {err}"))

        # Define the robust mock Supabase script
        mock_supabase_script = """
        (() => {
            const mockClient = {
                auth: {
                    onAuthStateChange: (callback) => {
                        window.authCallback = callback;
                        // Start as LOGGED OUT (null session)
                        setTimeout(() => {
                            callback('SIGNED_OUT', null);
                        }, 100);
                        return { data: { subscription: { unsubscribe: () => {} } } };
                    },
                    getSession: async () => ({ data: { session: null }, error: null }),
                    getUser: async () => ({ data: { user: null }, error: null }),
                    signOut: async () => ({ error: null }),
                    signInWithPassword: async ({ email, password }) => {
                        setTimeout(() => {
                            if (window.authCallback) {
                                window.authCallback('SIGNED_IN', {
                                    user: { email: email, id: '123' },
                                    session: { user: { email: email, id: '123' } }
                                });
                            }
                        }, 50);
                        return { data: { user: { email, id: '123' } }, error: null };
                    }
                },
                from: (table) => ({
                    select: () => ({
                        eq: () => ({ order: () => Promise.resolve({ data: mockReleases, error: null }) }),
                        order: () => Promise.resolve({ data: mockReleases, error: null }),
                        or: () => ({ order: () => Promise.resolve({ data: mockReleases, error: null }) })
                    })
                }),
                storage: {
                    from: () => ({
                        getPublicUrl: () => ({ data: { publicUrl: 'mock-url' } })
                    })
                }
            };
            const mockReleases = [
                {
                    id: 1,
                    nome: "João José Nassif Oliveira Mokarzel",
                    permanente: true,
                    periodo_inicio: null,
                    periodo_fim: null,
                    observacao: "Está autorizado pela Amanda, João José Nassif Oliveira Mokarzel a estacionar no subsolo somente as segundas e sextas-feiras",
                    criador_nome: "armandodecamposjr@gmail.com",
                    created_at: "2026-08-07T16:02:56.000Z",
                    concluida: false,
                    concluida_por: null,
                    concluida_em: null,
                    anexo_url: null,
                    user_id: "123"
                },
                {
                    id: 2,
                    nome: "Maria Eduarda Ferreira Saraiva",
                    permanente: true,
                    periodo_inicio: null,
                    periodo_fim: null,
                    observacao: "Liberar toda segunda\\nNome : Maria Eduarda Ferreira Saraiva\\nCel : 19989556278\\nCPF: 48789611802\\nLuizgustavo1646@gmail.com\\nLiberação da Carol do BEES",
                    criador_nome: "armandodecamposjr@gmail.com",
                    created_at: "2026-08-07T10:44:40.000Z",
                    concluida: false,
                    concluida_por: null,
                    concluida_em: null,
                    anexo_url: null,
                    user_id: "456"
                }
            ];

            // Lock the supabase object so CDN script can't overwrite it
            Object.defineProperty(window, 'supabase', {
                value: { createClient: () => mockClient },
                writable: false,
                configurable: false
            });
        })();
        """

        await page.add_init_script(mock_supabase_script)

        file_path = f"file://{os.getcwd()}/index.htm"
        await page.goto(file_path)

        # Wait until page loaded in logged-out state and list is visible
        print("Waiting for page loaded in logged-out state...")
        await page.wait_for_selector("#liberacao-page", state="visible", timeout=5000)
        await asyncio.sleep(1)
        await page.screenshot(path="logged_out.png")
        print("Captured logged_out.png successfully.")

        # 1. Click "Fazer Login" button
        print("Clicking Fazer Login button...")
        await page.click("#sign-in-top")
        await page.wait_for_selector("#auth-container", state="visible", timeout=5000)
        await asyncio.sleep(1)
        await page.screenshot(path="login_modal_open.png")
        print("Captured login_modal_open.png successfully.")

        # 2. Perform a simulated login form submission
        print("Entering credentials and submitting...")
        await page.fill("#email", "test@example.com")
        await page.fill("#password", "password123")
        await page.click("#submit-btn")

        # Wait for #auth-container to be hidden and logged-in UI to display
        await page.wait_for_selector("#auth-container", state="hidden", timeout=5000)
        await asyncio.sleep(1)
        await page.screenshot(path="logged_in.png")
        print("Captured logged_in.png successfully.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())
