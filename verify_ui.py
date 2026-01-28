import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1000})
        page = await context.new_page()

        mock_supabase_script = """
        (() => {
            const mockClient = {
                auth: {
                    onAuthStateChange: (callback) => {
                        setTimeout(() => {
                            callback('SIGNED_IN', {
                                user: { email: 'test@example.com', id: '123' },
                                session: { user: { email: 'test@example.com', id: '123' } }
                            });
                        }, 100);
                        return { data: { subscription: { unsubscribe: () => {} } } };
                    },
                    getSession: async () => ({ data: { session: { user: { email: 'test@example.com', id: '123' } } }, error: null }),
                    getUser: async () => ({ data: { user: { email: 'test@example.com', id: '123' } }, error: null }),
                    signOut: async () => ({ error: null }),
                },
                from: (table) => ({
                    select: () => ({
                        eq: () => ({ order: () => Promise.resolve({ data: [], error: null }) }),
                        order: () => Promise.resolve({ data: [], error: null })
                    })
                })
            };
            window.supabase = { createClient: () => mockClient };
        })();
        """

        await page.add_init_script(mock_supabase_script)

        file_path = f"file://{os.getcwd()}/index.htm"
        await page.goto(file_path)
        await page.wait_for_selector("#liberacao-page", state="visible", timeout=5000)

        # Give it a moment to render the header
        await asyncio.sleep(1)

        # Check background color of #liberacao-header-fixed
        bg_color = await page.evaluate('''() => {
            const el = document.getElementById('liberacao-header-fixed');
            return window.getComputedStyle(el).backgroundColor;
        }''')
        print(f"Background color of header: {bg_color}")

        await page.screenshot(path="verification_no_bg.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())
