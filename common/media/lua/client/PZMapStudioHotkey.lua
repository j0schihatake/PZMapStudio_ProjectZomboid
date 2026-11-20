-- F10 prints the Java bridge status and command help.
local function api()
    if PZMapStudioAPI then
        return PZMapStudioAPI.getInstance()
    end
    return nil
end

-- F10 is handled by PZMapStudioPanel.lua; keep startup logging here.
local function showHelp()
    local a = api()
    if not a then
        print("[PZMapStudio] Java API not loaded. Approve PZMapStudio.jar in ZombieBuddy if asked.")
        return
    end
    print("[PZMapStudio] " .. a:status())
    print("[PZMapStudio] " .. a:help())
end

Events.OnGameStart.Add(showHelp)

local pollTicks = 0
Events.OnTick.Add(function()
    pollTicks = pollTicks + 1
    if pollTicks % 120 == 0 and PZMapStudioAPI then
        local response = PZMapStudioAPI.getInstance():pollAgentQueue()
        if response and response ~= "" then
            print("[PZMapStudio] queue: " .. response)
        end
    end
end)

Events.OnKeyPressed.Add(function(key)
    if key == Keyboard.KEY_F11 and PZMapStudioAPI then
        print("[PZMapStudio] " .. PZMapStudioAPI.getInstance():observe())
    end
end)
