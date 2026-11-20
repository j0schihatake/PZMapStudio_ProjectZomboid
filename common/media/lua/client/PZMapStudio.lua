-- Minimal in-game bridge. The Java core is exposed by javaPkgName.
local function api()
    if PZMapStudioAPI then
        return PZMapStudioAPI.getInstance()
    end
    return nil
end

local function announce()
    local a = api()
    if not a then
        print("[PZMapStudio] Java API not loaded; approve the JAR if ZombieBuddy asks.")
        return
    end
    print("[PZMapStudio] " .. a:status())
    print("[PZMapStudio] " .. a:help())
end

Events.OnGameStart.Add(announce)
Events.OnMainMenuEnter.Add(announce)
